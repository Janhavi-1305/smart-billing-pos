# Smart Billing & POS System

A retail billing and inventory management system built with **FastAPI, SQLAlchemy and PostgreSQL**. It handles products, customers and invoices, validates stock before every sale, and supports bulk product import and report export through Excel.

> Developed as a B.Tech (AI & Data Science) project at DKTE Society's Textile and Engineering Institute, Ichalkaranji.

---

## Features

- **Product management**: name, SKU, category, cost price, selling price, stock quantity and unit.
- **Customer and invoice management**: create invoices linked to customers, with discounts and payment method.
- **Stock validation**: checks available stock before an invoice is saved. Repeated lines for the same product are combined before the check.
- **Transaction-safe invoicing**: invoice and stock updates are committed together, so a failed request never leaves partial data.
- **Clear errors**: product-specific stock shortfall messages and row-specific Excel import errors.
- **Excel import**: bulk upload products from `.xlsx` with header and row validation. Invalid rows are skipped and reported.
- **Excel export**: download styled workbooks of products and invoices (invoice number, customer, total, payment status, created time).
- **Dashboard**: total revenue, gross profit, expenses, net profit, low-stock alerts and sales by category.
- **POS billing screen**: product search, category filters, cart, and printable receipts.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy (ORM) |
| Excel | openpyxl |
| File uploads | python-multipart |
| API testing | Swagger UI (`/docs`), Postman |
| Tools | Git, GitHub, VS Code |


## How It Works

**Invoice flow**

```
Invoice request
  -> combine duplicate product lines
  -> check stock availability
  -> write invoice + update stock in one transaction
  -> return invoice, or a product-level stock shortfall error
```

**Excel import flow**

```
Upload .xlsx
  -> validate file type and headers
  -> validate each row
  -> insert valid rows
  -> return imported / skipped counts with row errors
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Janhavi-1305/<your-repo-name>.git
cd <your-repo-name>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Database setup

Create a PostgreSQL database (the project uses `smart_billing_pos` by default):

```sql
CREATE DATABASE smart_billing_pos;
```

Set the connection string as an environment variable (or in a `.env` file). **Never commit credentials.**

```bash
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/smart_billing_pos
```

### Run the server

```bash
uvicorn app.main:app --reload
```

Then open the API docs (Swagger UI) at http://127.0.0.1:8000/docs

## Excel Import Format

The product import expects an `.xlsx` file with these column headers:

| name | sku | category | price | cost_price | stock_quantity | unit |
|---|---|---|---|---|---|---|
| Rice | RIC-01 | Grocery | 60 | 45 | 100 | kg |

Rows with missing or invalid values are skipped, and the response lists the reason for each skipped row.

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLAlchemy engine, session, get_db dependency
│   ├── models/          # Product, Customer, Invoice models
│   ├── routes/          # API route handlers
│   └── services/        # Stock validation, Excel import/export
├── requirements.txt
└── README.md
```

## Roadmap

- [ ] ML-based demand forecasting using historical sales data
- [ ] Authentication and role-based access
- [ ] Supplier management
- [ ] Scheduled sales reports
- [ ] Automated tests for invoice and import workflows

## Author

**Janhavi Sunil Nazare**
B.Tech, Artificial Intelligence & Data Science, DKTE (2023-2027)

GitHub: [Janhavi-1305](https://github.com/Janhavi-1305) | LinkedIn: [janhavi-nazare](https://www.linkedin.com/in/janhavi-nazare/)
