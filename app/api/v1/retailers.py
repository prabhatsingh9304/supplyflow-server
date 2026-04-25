import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.retailer import (
    RetailerCreateRequest,
    RetailerListResponse,
    RetailerResponse,
    RetailerUpdateRequest,
)
from app.services import retailer as retailer_service

router = APIRouter(prefix="/api/v1/retailers", tags=["Retailers"])

SupplierUser = Annotated[User, Depends(require_role("supplier"))]


@router.get("", response_model=RetailerListResponse)
async def list_retailers(
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await retailer_service.list_retailers(
        db, current_user.organization_id, skip, limit
    )


@router.post("", response_model=RetailerResponse, status_code=201)
async def create_retailer(
    data: RetailerCreateRequest,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await retailer_service.create_retailer(
        db, current_user.organization_id, data
    )


@router.get("/{retailer_id}", response_model=RetailerResponse)
async def get_retailer(
    retailer_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await retailer_service.get_retailer(
        db, retailer_id, current_user.organization_id
    )


@router.patch("/{retailer_id}", response_model=RetailerResponse)
async def update_retailer(
    retailer_id: uuid.UUID,
    data: RetailerUpdateRequest,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await retailer_service.update_retailer(
        db, retailer_id, current_user.organization_id, data
    )


@router.delete("/{retailer_id}")
async def delete_retailer(
    retailer_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await retailer_service.delete_retailer(
        db, retailer_id, current_user.organization_id
    )
