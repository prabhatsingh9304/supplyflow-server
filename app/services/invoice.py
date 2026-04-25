import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.invoice import Invoice
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.organization import Organization
from app.models.retailer import Retailer
from app.models.user import User
from app.repositories import invoice as invoice_repo
from app.schemas.invoice import InvoiceResponse
from app.utils.pdf import generate_invoice_pdf, schedule_pdf_cleanup


async def generate_invoice(
    db: AsyncSession, order_id: uuid.UUID, user: User
) -> InvoiceResponse:
    order = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order_id, Order.organization_id == user.organization_id)
    )
    order = order.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if order.status not in (OrderStatus.accepted, OrderStatus.delivered):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice can only be generated for accepted or delivered orders. Current: {order.status.value}",
        )

    existing = await invoice_repo.get_invoice_by_order_id(
        db, order_id, user.organization_id
    )
    if existing:
        return InvoiceResponse.model_validate(existing)

    org = await db.get(Organization, user.organization_id)
    retailer = await db.execute(
        select(Retailer).where(Retailer.id == order.retailer_id)
    )
    retailer = retailer.scalar_one()
    retailer_user = await db.execute(
        select(User).where(User.id == retailer.user_id)
    )
    retailer_user = retailer_user.scalar_one()

    invoice_no = await invoice_repo.get_next_invoice_number(db, user.organization_id)

    items_data = []
    for item in order.items:
        items_data.append({
            "name": item.product.name if item.product else "Unknown",
            "qty": item.qty,
            "price": item.price,
            "gst_percent": item.product.gst_percent if item.product else 0,
        })

    pdf_path = generate_invoice_pdf(
        invoice_no=invoice_no,
        org_name=org.name,
        org_phone=org.phone,
        org_gst=org.gst_number,
        org_address=org.address,
        order_date=order.created_at,
        retailer_name=retailer_user.name,
        retailer_shop=retailer.shop_name,
        retailer_address=retailer.address,
        retailer_phone=retailer_user.phone,
        items=items_data,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
    )
    schedule_pdf_cleanup(pdf_path)

    invoice = await invoice_repo.create_invoice(
        db,
        organization_id=user.organization_id,
        order_id=order.id,
        invoice_no=invoice_no,
        total=order.total,
        pdf_path=pdf_path,
    )

    return InvoiceResponse.model_validate(invoice)


async def get_invoice(
    db: AsyncSession, invoice_id: uuid.UUID, organization_id: uuid.UUID
) -> InvoiceResponse:
    invoice = await invoice_repo.get_invoice_by_id(db, invoice_id, organization_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    return InvoiceResponse.model_validate(invoice)


async def get_invoice_pdf_path(
    db: AsyncSession, invoice_id: uuid.UUID, organization_id: uuid.UUID
) -> str:
    invoice = await invoice_repo.get_invoice_by_id(db, invoice_id, organization_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    if not invoice.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDF not generated"
        )
    return invoice.pdf_path
