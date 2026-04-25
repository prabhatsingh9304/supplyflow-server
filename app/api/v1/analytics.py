from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.analytics import (
    DashboardResponse,
    RevenueResponse,
    TopProductsResponse,
    TopRetailersResponse,
)
from app.services import analytics as analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

SupplierUser = Annotated[User, Depends(require_role("supplier"))]


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await analytics_service.get_dashboard(db, current_user.organization_id)


@router.get("/revenue", response_model=RevenueResponse)
async def revenue(
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await analytics_service.get_revenue(db, current_user.organization_id)


@router.get("/top-products", response_model=TopProductsResponse)
async def top_products(
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    return await analytics_service.get_top_products(
        db, current_user.organization_id, limit
    )


@router.get("/top-retailers", response_model=TopRetailersResponse)
async def top_retailers(
    current_user: SupplierUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    return await analytics_service.get_top_retailers(
        db, current_user.organization_id, limit
    )
