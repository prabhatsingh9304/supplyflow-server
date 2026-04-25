import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


async def get_invoice_by_id(
    db: AsyncSession, invoice_id: uuid.UUID, organization_id: uuid.UUID
) -> Invoice | None:
    result = await db.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def get_invoice_by_order_id(
    db: AsyncSession, order_id: uuid.UUID, organization_id: uuid.UUID
) -> Invoice | None:
    result = await db.execute(
        select(Invoice).where(
            Invoice.order_id == order_id,
            Invoice.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def get_next_invoice_number(db: AsyncSession, organization_id: uuid.UUID) -> str:
    result = await db.execute(
        select(func.count())
        .select_from(Invoice)
        .where(Invoice.organization_id == organization_id)
    )
    count = result.scalar_one()
    return f"INV-{count + 1:06d}"


async def create_invoice(db: AsyncSession, **kwargs) -> Invoice:
    invoice = Invoice(**kwargs)
    db.add(invoice)
    await db.flush()
    return invoice
