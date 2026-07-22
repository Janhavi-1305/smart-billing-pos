from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import (  # noqa: F401 — register models with SQLAlchemy metadata
    Customer,
    Expense,
    Invoice,
    InvoiceItem,
    Product,
    StockTransaction,
)
from app.routes import customers, health, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Smart Billing POS API",
    description="Backend API for billing and point-of-sale operations",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(customers.router)
