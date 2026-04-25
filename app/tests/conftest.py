import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

engine_test = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def supplier_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register-supplier",
        json={
            "name": "Test Supplier",
            "phone": "1111111111",
            "password": "testpass123",
            "organization_name": "Test Org",
            "gst_number": "GST999",
        },
    )
    assert resp.status_code == 201

    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "1111111111", "password": "testpass123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="session")
async def retailer_data(client: AsyncClient, supplier_token: str) -> dict:
    resp = await client.post(
        "/api/v1/retailers",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={
            "name": "Test Retailer",
            "phone": "2222222222",
            "pin": "5678",
            "shop_name": "Test Shop",
            "address": "456 Test Ave",
            "credit_limit": 10000,
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture(scope="session")
async def retailer_token(client: AsyncClient, retailer_data: dict) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "2222222222", "password": "5678"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="session")
async def product_data(client: AsyncClient, supplier_token: str) -> dict:
    resp = await client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={
            "name": "Test Product",
            "sku": "TP-001",
            "category": "Testing",
            "price": 100,
            "stock": 500,
            "gst_percent": 18,
        },
    )
    assert resp.status_code == 201
    return resp.json()
