import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.retailer import Retailer


async def get_orders(
    db: AsyncSession,
    organization_id: uuid.UUID,
    retailer_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Order], int]:
    base_filter = [Order.organization_id == organization_id]
    if retailer_id is not None:
        base_filter.append(Order.retailer_id == retailer_id)

    count_q = select(func.count()).select_from(Order).where(*base_filter)
    total = (await db.execute(count_q)).scalar_one()

    q = (
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.retailer).selectinload(Retailer.user),
        )
        .where(*base_filter)
        .offset(skip)
        .limit(limit)
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(q)
    return list(result.scalars().unique().all()), total


async def get_order_by_id(
    db: AsyncSession, order_id: uuid.UUID, organization_id: uuid.UUID
) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.retailer).selectinload(Retailer.user),
        )
        .where(Order.id == order_id, Order.organization_id == organization_id)
    )
    return result.scalar_one_or_none()


async def create_order(db: AsyncSession, **kwargs) -> Order:
    order = Order(**kwargs)
    db.add(order)
    await db.flush()
    return order


async def create_order_item(db: AsyncSession, **kwargs) -> OrderItem:
    item = OrderItem(**kwargs)
    db.add(item)
    await db.flush()
    return item
