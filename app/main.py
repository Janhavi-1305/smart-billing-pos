from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
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
from app.routes import customers, health, invoices, products
from app.routes import customers, health, invoices, products, import_export

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(import_export.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(invoices.router)