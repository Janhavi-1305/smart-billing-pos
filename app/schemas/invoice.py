from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class InvoiceCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: list[InvoiceItemCreate] = Field(..., min_length=1)


class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    invoice_number: str
    total_amount: Decimal
    payment_status: str
    payment_method: str | None
    created_at: datetime
    items: list[InvoiceItemResponse]


class InvoiceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str
    invoice_number: str
    total_amount: Decimal
    payment_status: str
    payment_method: str | None
    created_at: datetime
