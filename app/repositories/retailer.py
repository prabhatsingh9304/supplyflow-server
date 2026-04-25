import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.retailer import Retailer


async def get_retailers(
    db: AsyncSession, organization_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> tuple[list[Retailer], int]:
    count_q = select(func.count()).select_from(Retailer).where(
        Retailer.organization_id == organization_id
    )
    total = (await db.execute(count_q)).scalar_one()

    q = (
        select(Retailer)
        .where(Retailer.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
        .order_by(Retailer.created_at.desc())
    )
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def get_retailer_by_id(
    db: AsyncSession, retailer_id: uuid.UUID, organization_id: uuid.UUID
) -> Retailer | None:
    result = await db.execute(
        select(Retailer).where(
            Retailer.id == retailer_id,
            Retailer.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def create_retailer(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    shop_name: str,
    address: str | None = None,
    credit_limit: Decimal = Decimal("0.00"),
) -> Retailer:
    retailer = Retailer(
        organization_id=organization_id,
        user_id=user_id,
        shop_name=shop_name,
        address=address,
        credit_limit=credit_limit,
    )
    db.add(retailer)
    await db.flush()
    return retailer


async def update_retailer(
    db: AsyncSession, retailer: Retailer, **kwargs
) -> Retailer:
    for key, value in kwargs.items():
        if value is not None:
            setattr(retailer, key, value)
    await db.flush()
    return retailer


async def delete_retailer(db: AsyncSession, retailer: Retailer) -> None:
    await db.delete(retailer)
    await db.flush()
