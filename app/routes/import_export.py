import io
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, Invoice, Customer

router = APIRouter(tags=["import-export"])

REQUIRED_COLUMNS = ["name", "sku", "category", "price", "cost_price", "stock_quantity", "unit"]


@router.post("/products/import")
async def import_products(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be a .xlsx file")

    contents = await file.read()
    workbook = load_workbook(filename=io.BytesIO(contents))
    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="File is empty")

    headers = [str(h).strip().lower() if h else "" for h in rows[0]]

    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

    col_index = {col: headers.index(col) for col in REQUIRED_COLUMNS}

    imported = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(rows[1:], start=2):
        try:
            name = row[col_index["name"]]
            sku = row[col_index["sku"]]
            category = row[col_index["category"]]
            price = row[col_index["price"]]
            cost_price = row[col_index["cost_price"]]
            stock_quantity = row[col_index["stock_quantity"]]
            unit = row[col_index["unit"]]

            if not name or price is None or stock_quantity is None:
                errors.append({"row": row_num, "reason": "Missing required value (name, price, or stock_quantity)"})
                skipped += 1
                continue

            product = Product(
                name=str(name),
                sku=str(sku) if sku else None,
                category=str(category) if category else None,
                price=float(price),
                cost_price=float(cost_price) if cost_price is not None else 0,
                stock_quantity=int(stock_quantity),
                unit=str(unit) if unit else "pcs",
            )
            db.add(product)
            imported += 1

        except (ValueError, TypeError) as e:
            errors.append({"row": row_num, "reason": f"Invalid data type: {str(e)}"})
            skipped += 1

    db.commit()

    return {"imported": imported, "skipped": skipped, "errors": errors}


@router.get("/products/export")
def export_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Products"

    headers = ["name", "sku", "category", "price", "cost_price", "stock_quantity", "unit"]
    sheet.append(headers)

    header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill

    for p in products:
        sheet.append([p.name, p.sku, p.category, float(p.price), float(p.cost_price), p.stock_quantity, p.unit])

    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)

    filename = f"products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/invoices/export")
def export_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).join(Customer).all()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Invoices"

    headers = ["invoice_number", "customer_name", "total_amount", "payment_status", "created_at"]
    sheet.append(headers)

    header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill

    for inv in invoices:
        sheet.append([
            inv.invoice_number,
            inv.customer.name,
            float(inv.total_amount),
            inv.payment_status,
            inv.created_at.strftime("%Y-%m-%d %H:%M:%S") if inv.created_at else "",
        ])

    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)

    filename = f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )