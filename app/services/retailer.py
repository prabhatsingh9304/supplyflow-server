import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories import retailer as retailer_repo
from app.repositories import user as user_repo
from app.schemas.retailer import (
    RetailerCreateRequest,
    RetailerListResponse,
    RetailerResponse,
    RetailerUpdateRequest,
)


def _to_response(retailer, user: User) -> RetailerResponse:
    return RetailerResponse(
        id=retailer.id,
        organization_id=retailer.organization_id,
        user_id=retailer.user_id,
        shop_name=retailer.shop_name,
        address=retailer.address,
        credit_limit=retailer.credit_limit,
        outstanding=retailer.outstanding,
        created_at=retailer.created_at,
        user_name=user.name,
        user_phone=user.phone,
        is_active=user.is_active,
    )


async def list_retailers(
    db: AsyncSession, organization_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> RetailerListResponse:
    retailers, total = await retailer_repo.get_retailers(
        db, organization_id, skip, limit
    )
    items = []
    for r in retailers:
        user = await user_repo.get_user_by_id(db, r.user_id)
        items.append(_to_response(r, user))
    return RetailerListResponse(items=items, total=total)


async def get_retailer(
    db: AsyncSession, retailer_id: uuid.UUID, organization_id: uuid.UUID
) -> RetailerResponse:
    retailer = await retailer_repo.get_retailer_by_id(db, retailer_id, organization_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Retailer not found"
        )
    user = await user_repo.get_user_by_id(db, retailer.user_id)
    return _to_response(retailer, user)


async def create_retailer(
    db: AsyncSession, organization_id: uuid.UUID, data: RetailerCreateRequest
) -> RetailerResponse:
    existing = await user_repo.get_user_by_phone(db, data.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    user = await user_repo.create_user(
        db,
        organization_id=organization_id,
        role=UserRole.retailer,
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.pin),
    )

    retailer = await retailer_repo.create_retailer(
        db,
        organization_id=organization_id,
        user_id=user.id,
        shop_name=data.shop_name,
        address=data.address,
        credit_limit=data.credit_limit,
    )

    return _to_response(retailer, user)


async def update_retailer(
    db: AsyncSession,
    retailer_id: uuid.UUID,
    organization_id: uuid.UUID,
    data: RetailerUpdateRequest,
) -> RetailerResponse:
    retailer = await retailer_repo.get_retailer_by_id(db, retailer_id, organization_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Retailer not found"
        )

    user = await user_repo.get_user_by_id(db, retailer.user_id)

    if data.shop_name is not None:
        retailer.shop_name = data.shop_name
    if data.address is not None:
        retailer.address = data.address
    if data.credit_limit is not None:
        retailer.credit_limit = data.credit_limit

    if data.name is not None:
        user.name = data.name
    if data.phone is not None:
        user.phone = data.phone
    if data.pin is not None:
        user.password_hash = hash_password(data.pin)
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.flush()
    return _to_response(retailer, user)


async def delete_retailer(
    db: AsyncSession, retailer_id: uuid.UUID, organization_id: uuid.UUID
) -> dict:
    retailer = await retailer_repo.get_retailer_by_id(db, retailer_id, organization_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Retailer not found"
        )

    user = await user_repo.get_user_by_id(db, retailer.user_id)
    user.is_active = False
    await db.flush()

    return {"message": "Retailer deactivated"}
