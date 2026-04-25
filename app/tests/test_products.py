import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, supplier_token: str):
    resp = await client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={
            "name": "Another Product",
            "sku": "AP-001",
            "price": 50,
            "stock": 200,
            "gst_percent": 12,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Another Product"
    assert data["stock"] == 200


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, supplier_token: str, product_data: dict):
    resp = await client.get(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, supplier_token: str, product_data: dict):
    resp = await client.get(
        f"/api/v1/products/{product_data['id']}",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == product_data["id"]


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, supplier_token: str, product_data: dict):
    resp = await client.patch(
        f"/api/v1/products/{product_data['id']}",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"price": 120},
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == "120"


@pytest.mark.asyncio
async def test_stock_update(client: AsyncClient, supplier_token: str, product_data: dict):
    resp = await client.post(
        f"/api/v1/products/{product_data['id']}/stock",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"quantity": 50},
    )
    assert resp.status_code == 200
    assert resp.json()["stock"] >= 50


@pytest.mark.asyncio
async def test_stock_insufficient(client: AsyncClient, supplier_token: str, product_data: dict):
    resp = await client.post(
        f"/api/v1/products/{product_data['id']}/stock",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"quantity": -999999},
    )
    assert resp.status_code == 400
