# SupplyFlow — Supplier & Retailer Ordering Platform Backend

A production-ready B2B ordering and billing platform backend built with FastAPI, PostgreSQL, and Docker Compose.

## Tech Stack

- **Python 3.12** / **FastAPI** / **Uvicorn**
- **SQLAlchemy 2.0** (async) / **Alembic**
- **PostgreSQL 16**
- **JWT** auth with **bcrypt** password hashing
- **Docker Compose**

## Quick Start

```bash
# 1. Copy env file
cp .env.example .env

# 2. Build and start services
docker compose up --build

# 3. API docs
open http://localhost:8000/docs
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── core/                # Config, DB, security, dependencies
│   ├── api/v1/              # Route handlers
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic v2 schemas
│   ├── services/            # Business logic
│   ├── repositories/        # Database access layer
│   ├── utils/               # Helpers
│   └── tests/               # Test suite
├── alembic/                 # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## API Modules

| Module | Endpoints | Access |
|--------|-----------|--------|
| Auth | register-supplier, login, me, change-password | Public / Authenticated |
| Retailers | CRUD | Supplier only |
| Products | CRUD + stock update | Supplier only |
| Orders | create, list, status update | Retailer creates, Supplier manages |
| Invoices | generate, view, download PDF | Supplier |
| Analytics | dashboard, revenue, top products/retailers | Supplier only |

## Multi-Tenancy

Each supplier is an organization. All data is scoped by `organization_id` and tenant isolation is enforced at every query.
