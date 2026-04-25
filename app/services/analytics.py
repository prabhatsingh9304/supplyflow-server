import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.retailer import Retailer
from app.schemas.analytics import (
    DashboardResponse,
    RevenueResponse,
    TopProductItem,
    TopProductsResponse,
    TopRetailerItem,
    TopRetailersResponse,
)


async def get_dashboard(db: AsyncSession, organization_id: uuid.UUID) -> DashboardResponse:
    total_retailers = (
        await db.execute(
            select(func.count())
            .select_from(Retailer)
            .where(Retailer.organization_id == organization_id)
        )
    ).scalar_one()

    total_products = (
        await db.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.organization_id == organization_id, Product.is_active.is_(True))
        )
    ).scalar_one()

    total_orders = (
        await db.execute(
            select(func.count())
            .select_from(Order)
            .where(Order.organization_id == organization_id)
        )
    ).scalar_one()

    total_revenue = (
        await db.execute(
            select(func.coalesce(func.sum(Order.total), 0))
            .where(
                Order.organization_id == organization_id,
                Order.status == OrderStatus.delivered,
            )
        )
    ).scalar_one()

    pending_orders = (
        await db.execute(
            select(func.count())
            .select_from(Order)
            .where(
                Order.organization_id == organization_id,
                Order.status == OrderStatus.pending,
            )
        )
    ).scalar_one()

    delivered_orders = (
        await db.execute(
            select(func.count())
            .select_from(Order)
            .where(
                Order.organization_id == organization_id,
                Order.status == OrderStatus.delivered,
            )
        )
    ).scalar_one()

    return DashboardResponse(
        total_retailers=total_retailers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=Decimal(str(total_revenue)),
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
    )


async def get_revenue(db: AsyncSession, organization_id: uuid.UUID) -> RevenueResponse:
    result = await db.execute(
        select(
            func.coalesce(func.sum(Order.total), 0),
            func.coalesce(func.sum(Order.tax), 0),
            func.count(),
        )
        .where(
            Order.organization_id == organization_id,
            Order.status == OrderStatus.delivered,
        )
    )
    row = result.one()
    return RevenueResponse(
        total_revenue=Decimal(str(row[0])),
        total_tax=Decimal(str(row[1])),
        total_orders=row[2],
    )


async def get_top_products(
    db: AsyncSession, organization_id: uuid.UUID, limit: int = 10
) -> TopProductsResponse:
    q = (
        select(
            Product.id,
            Product.name,
            func.coalesce(func.sum(OrderItem.qty), 0).label("total_qty"),
            func.coalesce(func.sum(OrderItem.price * OrderItem.qty), 0).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(
            Product.organization_id == organization_id,
            Order.status == OrderStatus.delivered,
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.qty).desc())
        .limit(limit)
    )
    result = await db.execute(q)
    items = [
        TopProductItem(
            product_id=str(row[0]),
            product_name=row[1],
            total_qty=int(row[2]),
            total_revenue=Decimal(str(row[3])),
        )
        for row in result.all()
    ]
    return TopProductsResponse(items=items)


async def get_top_retailers(
    db: AsyncSession, organization_id: uuid.UUID, limit: int = 10
) -> TopRetailersResponse:
    q = (
        select(
            Retailer.id,
            Retailer.shop_name,
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.total), 0).label("total_spent"),
        )
        .join(Order, Order.retailer_id == Retailer.id)
        .where(
            Retailer.organization_id == organization_id,
            Order.status == OrderStatus.delivered,
        )
        .group_by(Retailer.id, Retailer.shop_name)
        .order_by(func.sum(Order.total).desc())
        .limit(limit)
    )
    result = await db.execute(q)
    items = [
        TopRetailerItem(
            retailer_id=str(row[0]),
            shop_name=row[1],
            total_orders=row[2],
            total_spent=Decimal(str(row[3])),
        )
        for row in result.all()
    ]
    return TopRetailersResponse(items=items)
