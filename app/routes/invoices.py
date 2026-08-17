from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceListResponse, InvoiceResponse
from app.services import invoice_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceListResponse])
def list_invoices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[InvoiceListResponse]:
    return invoice_service.get_invoices(db, skip=skip, limit=limit)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> InvoiceResponse:
    invoice = invoice_service.get_invoice(db, invoice_id)
    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with id {invoice_id} not found",
        )
    return invoice_service.build_invoice_response(invoice)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_in: InvoiceCreate, db: Session = Depends(get_db)
) -> InvoiceResponse:
    try:
        return invoice_service.create_invoice(db, invoice_in)
    except invoice_service.CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {exc.customer_id} not found",
        ) from exc
    except invoice_service.ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "One or more products not found",
                "product_ids": exc.product_ids,
            },
        ) from exc
    except invoice_service.InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Insufficient stock for one or more products",
                "items": exc.items,
            },
        ) from exc
