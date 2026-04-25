import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_invoice(
    client: AsyncClient, supplier_token: str, retailer_token: str, product_data: dict
):
    order_resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 3}]},
    )
    assert order_resp.status_code == 201
    order_id = order_resp.json()["id"]

    await client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"status": "accepted"},
    )

    resp = await client.post(
        f"/api/v1/invoices/{order_id}/generate",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["invoice_no"].startswith("INV-")
    assert data["order_id"] == order_id
    assert data["pdf_path"] is not None


@pytest.mark.asyncio
async def test_get_invoice(
    client: AsyncClient, supplier_token: str, retailer_token: str, product_data: dict
):
    order_resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 1}]},
    )
    order_id = order_resp.json()["id"]

    await client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {supplier_token}"},
        json={"status": "accepted"},
    )

    gen_resp = await client.post(
        f"/api/v1/invoices/{order_id}/generate",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    invoice_id = gen_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == invoice_id


@pytest.mark.asyncio
async def test_invoice_requires_accepted_or_delivered(
    client: AsyncClient, supplier_token: str, retailer_token: str, product_data: dict
):
    order_resp = await client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"items": [{"product_id": product_data["id"], "qty": 1}]},
    )
    order_id = order_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/invoices/{order_id}/generate",
        headers={"Authorization": f"Bearer {supplier_token}"},
    )
    assert resp.status_code == 400
