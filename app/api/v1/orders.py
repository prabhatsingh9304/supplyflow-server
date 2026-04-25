import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.order import (
    OrderCreateRequest,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdateRequest,
    SupplierOrderCreateRequest,
)
from app.services import order as order_service

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.get("", response_model=OrderListResponse)
async def list_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await order_service.list_orders(db, current_user, skip, limit)


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await order_service.create_order(db, current_user, data)


@router.post("/manual", response_model=OrderResponse, status_code=201)
async def create_manual_order(
    data: SupplierOrderCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await order_service.create_order_for_retailer(db, current_user, data)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await order_service.get_order(db, order_id, current_user)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await order_service.update_order_status(db, order_id, current_user, data)
