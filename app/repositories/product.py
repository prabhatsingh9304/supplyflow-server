import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def get_products(
    db: AsyncSession,
    organization_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    active_only: bool = False,
) -> tuple[list[Product], int]:
    base = select(Product).where(Product.organization_id == organization_id)
    count_base = select(func.count()).select_from(Product).where(
        Product.organization_id == organization_id
    )

    if active_only:
        base = base.where(Product.is_active.is_(True))
        count_base = count_base.where(Product.is_active.is_(True))

    total = (await db.execute(count_base)).scalar_one()

    q = base.offset(skip).limit(limit).order_by(Product.name)
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def get_product_by_id(
    db: AsyncSession, product_id: uuid.UUID, organization_id: uuid.UUID
) -> Product | None:
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def create_product(db: AsyncSession, organization_id: uuid.UUID, **kwargs) -> Product:
    product = Product(organization_id=organization_id, **kwargs)
    db.add(product)
    await db.flush()
    return product


async def update_product(db: AsyncSession, product: Product, **kwargs) -> Product:
    for key, value in kwargs.items():
        if value is not None:
            setattr(product, key, value)
    await db.flush()
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.flush()
