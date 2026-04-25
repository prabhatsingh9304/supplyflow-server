import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
    StockUpdateRequest,
)
from app.services import product as product_service

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

SupplierUser = Annotated[User, Depends(require_role("supplier"))]
CatalogUser = Annotated[User, Depends(require_role("supplier", "retailer"))]


@router.get("", response_model=ProductListResponse)
async def list_products(
    current_user: CatalogUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await product_service.list_products(
        db, current_user.organization_id, skip, limit
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreateRequest,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await product_service.create_product(
        db, current_user.organization_id, data
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await product_service.get_product(
        db, product_id, current_user.organization_id
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdateRequest,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await product_service.update_product(
        db, product_id, current_user.organization_id, data
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await product_service.delete_product(
        db, product_id, current_user.organization_id
    )


@router.post("/{product_id}/stock", response_model=ProductResponse)
async def update_stock(
    product_id: uuid.UUID,
    data: StockUpdateRequest,
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await product_service.update_stock(
        db, product_id, current_user.organization_id, data
    )
