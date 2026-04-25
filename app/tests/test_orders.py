import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_place_order(
    client: AsyncClient, retailer_token: str, product_data: dict
):
    resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 2}]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["qty"] == 2


@pytest.mark.asyncio
async def test_supplier_cannot_place_order(
    client: AsyncClient, supplier_token: str, product_data: dict
):
    resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 1}]},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_order_status_lifecycle(
    client: AsyncClient, supplier_token: str, retailer_token: str, product_data: dict
):
    create_resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 1}]},
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    for next_status in ["accepted", "packed", "dispatched", "delivered"]:
        resp = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {supplier_token}"},
            json={"status": next_status},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == next_status


@pytest.mark.asyncio
async def test_invalid_status_transition(
    client: AsyncClient, supplier_token: str, retailer_token: str, product_data: dict
):
    create_resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 1}]},
    )
    order_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"status": "delivered"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_orders_as_retailer(
    client: AsyncClient, retailer_token: str, product_data: dict
):
    resp = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
