import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_retailer(client: AsyncClient, supplier_token: str):
    resp = await client.post(
        "/api/v1/retailers",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={
            "name": "New Retailer",
            "phone": "4444444444",
            "pin": "9999",
            "shop_name": "New Shop",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["shop_name"] == "New Shop"
    assert data["user_name"] == "New Retailer"


@pytest.mark.asyncio
async def test_list_retailers(client: AsyncClient, supplier_token: str, retailer_data: dict):
    resp = await client.get(
        "/api/v1/retailers",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_retailer(client: AsyncClient, supplier_token: str, retailer_data: dict):
    resp = await client.get(
        f"/api/v1/retailers/{retailer_data['id']}",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == retailer_data["id"]


@pytest.mark.asyncio
async def test_update_retailer(client: AsyncClient, supplier_token: str, retailer_data: dict):
    resp = await client.patch(
        f"/api/v1/retailers/{retailer_data['id']}",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"shop_name": "Updated Shop"},
    )
    assert resp.status_code == 200
    assert resp.json()["shop_name"] == "Updated Shop"


@pytest.mark.asyncio
async def test_retailer_requires_supplier_role(client: AsyncClient, retailer_token: str):
    resp = await client.get(
        "/api/v1/retailers",
        headers={"Authorization": f"Bearer {retailer_token}"},
    )
    assert resp.status_code == 403
