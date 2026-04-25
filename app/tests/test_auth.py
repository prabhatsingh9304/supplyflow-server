import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_supplier(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register-supplier",
        json={
            "name": "Auth Test Supplier",
            "phone": "3333333333",
            "password": "authpass123",
            "organization_name": "Auth Org",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "supplier"
    assert data["phone"] == "3333333333"


@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register-supplier",
        json={
            "name": "Dup Supplier",
            "phone": "3333333333",
            "password": "duppass123",
            "organization_name": "Dup Org",
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "3333333333", "password": "authpass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "3333333333", "password": "wrongpass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"phone": "3333333333", "password": "authpass123"},
    )
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["phone"] == "3333333333"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"phone": "3333333333", "password": "authpass123"},
    )
    token = login.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"old_password": "authpass123", "new_password": "newauth456"},
    )
    assert resp.status_code == 200

    login2 = await client.post(
        "/api/v1/auth/login",
        json={"phone": "3333333333", "password": "newauth456"},
    )
    assert login2.status_code == 200
