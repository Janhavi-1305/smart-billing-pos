from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.product import Product
from app.schemas.invoice import InvoiceCreate, InvoiceItemResponse, InvoiceListResponse, InvoiceResponse


class InsufficientStockError(Exception):
    def __init__(self, items: list[dict[str, int | str]]):
        self.items = items
        super().__init__("Insufficient stock for one or more products")


class CustomerNotFoundError(Exception):
    def __init__(self, customer_id: int):
        self.customer_id = customer_id
        super().__init__(f"Customer with id {customer_id} not found")


class ProductNotFoundError(Exception):
    def __init__(self, product_ids: list[int]):
        self.product_ids = product_ids
        super().__init__("One or more products not found")


def _generate_invoice_number(db: Session) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    prefix = f"INV-{today}-"
    count = (
        db.query(Invoice)
        .filter(Invoice.invoice_number.like(f"{prefix}%"))
        .count()
    )
    return f"{prefix}{count + 1:04d}"


def build_invoice_response(invoice: Invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id,
        customer_id=invoice.customer_id,
        invoice_number=invoice.invoice_number,
        total_amount=invoice.total_amount,
        payment_status=invoice.payment_status,
        payment_method=invoice.payment_method,
        created_at=invoice.created_at,
        items=[
            InvoiceItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in invoice.items
        ],
    )


def _to_invoice_list_response(invoice: Invoice) -> InvoiceListResponse:
    return InvoiceListResponse(
        id=invoice.id,
        customer_id=invoice.customer_id,
        customer_name=invoice.customer.name,
        invoice_number=invoice.invoice_number,
        total_amount=invoice.total_amount,
        payment_status=invoice.payment_status,
        payment_method=invoice.payment_method,
        created_at=invoice.created_at,
    )


def get_invoices(
    db: Session, skip: int = 0, limit: int = 100
) -> list[InvoiceListResponse]:
    invoices = (
        db.query(Invoice)
        .options(joinedload(Invoice.customer))
        .order_by(Invoice.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_invoice_list_response(invoice) for invoice in invoices]


def get_invoice(db: Session, invoice_id: int) -> Invoice | None:
    return (
        db.query(Invoice)
        .options(
            joinedload(Invoice.items).joinedload(InvoiceItem.product),
        )
        .filter(Invoice.id == invoice_id)
        .first()
    )


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> InvoiceResponse:
    customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first()
    if customer is None:
        raise CustomerNotFoundError(invoice_in.customer_id)

    product_ids = {item.product_id for item in invoice_in.items}
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    products_by_id = {product.id: product for product in products}

    missing_ids = sorted(product_ids - products_by_id.keys())
    if missing_ids:
        raise ProductNotFoundError(missing_ids)

    required_stock: dict[int, int] = defaultdict(int)
    for item in invoice_in.items:
        required_stock[item.product_id] += item.quantity

    stock_errors: list[dict[str, int | str]] = []
    for product_id, required_qty in required_stock.items():
        product = products_by_id[product_id]
        if product.stock_quantity < required_qty:
            stock_errors.append(
                {
                    "product_id": product_id,
                    "product_name": product.name,
                    "requested": required_qty,
                    "available": product.stock_quantity,
                }
            )

    if stock_errors:
        raise InsufficientStockError(stock_errors)

    total_amount = Decimal("0")
    line_items: list[tuple[Product, int, Decimal, Decimal]] = []

    for item in invoice_in.items:
        product = products_by_id[item.product_id]
        unit_price = product.price
        subtotal = unit_price * item.quantity
        total_amount += subtotal
        line_items.append((product, item.quantity, unit_price, subtotal))

    invoice = Invoice(
        customer_id=invoice_in.customer_id,
        invoice_number=_generate_invoice_number(db),
        total_amount=total_amount,
        payment_status="pending",
    )
    db.add(invoice)
    db.flush()

    for product, quantity, unit_price, subtotal in line_items:
        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
        )
        product.stock_quantity -= quantity

    db.commit()
    db.refresh(invoice)

    created = get_invoice(db, invoice.id)
    assert created is not None
    return build_invoice_response(created)
