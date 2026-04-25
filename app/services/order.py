import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.repositories import order as order_repo
from app.repositories import product as product_repo
from app.schemas.order import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdateRequest,
    SupplierOrderCreateRequest,
)

VALID_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.pending: [OrderStatus.accepted, OrderStatus.cancelled],
    OrderStatus.accepted: [OrderStatus.packed, OrderStatus.cancelled],
    OrderStatus.packed: [OrderStatus.dispatched, OrderStatus.cancelled],
    OrderStatus.dispatched: [OrderStatus.delivered],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: [],
}


def _order_to_response(order: Order) -> OrderResponse:
    items = []
    for item in order.items:
        items.append(
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name if item.product else "Unknown",
                qty=item.qty,
                price=item.price,
            )
        )
    retailer_name = ""
    retailer_phone = ""
    retailer_address = ""
    if order.retailer:
        retailer_address = order.retailer.address or ""
        if order.retailer.user:
            retailer_name = order.retailer.user.name
            retailer_phone = order.retailer.user.phone

    return OrderResponse(
        id=order.id,
        organization_id=order.organization_id,
        retailer_id=order.retailer_id,
        retailer_name=retailer_name,
        retailer_phone=retailer_phone,
        retailer_address=retailer_address,
        status=order.status,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        created_at=order.created_at,
        items=items,
    )


async def list_orders(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 50,
) -> OrderListResponse:
    retailer_id = None
    if user.role == UserRole.retailer:
        retailer = await _get_retailer_for_user(db, user)
        retailer_id = retailer.id

    orders, total = await order_repo.get_orders(
        db, user.organization_id, retailer_id=retailer_id, skip=skip, limit=limit
    )

    items = [_order_to_response(o) for o in orders]
    return OrderListResponse(items=items, total=total)


async def get_order(
    db: AsyncSession, order_id: uuid.UUID, user: User
) -> OrderResponse:
    order = await order_repo.get_order_by_id(db, order_id, user.organization_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if user.role == UserRole.retailer:
        retailer = await _get_retailer_for_user(db, user)
        if order.retailer_id != retailer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your order",
            )

    return _order_to_response(order)


async def create_order(
    db: AsyncSession, user: User, data: OrderCreateRequest
) -> OrderResponse:
    if user.role != UserRole.retailer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only retailers can place orders",
        )

    retailer = await _get_retailer_for_user(db, user)

    subtotal = Decimal("0.00")
    tax = Decimal("0.00")
    product_cache = {}

    for item_req in data.items:
        product = await product_repo.get_product_by_id(
            db, item_req.product_id, user.organization_id
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_req.product_id} not found",
            )
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not active",
            )
        if product.stock < item_req.qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}",
            )
        product_cache[item_req.product_id] = product
        line_subtotal = product.price * item_req.qty
        line_tax = line_subtotal * product.gst_percent / Decimal("100")
        subtotal += line_subtotal
        tax += line_tax

    total = subtotal + tax

    order = await order_repo.create_order(
        db,
        organization_id=user.organization_id,
        retailer_id=retailer.id,
        status=OrderStatus.pending,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )

    for item_req in data.items:
        product = product_cache[item_req.product_id]
        await order_repo.create_order_item(
            db,
            order_id=order.id,
            product_id=item_req.product_id,
            qty=item_req.qty,
            price=product.price,
        )

    refreshed = await order_repo.get_order_by_id(db, order.id, user.organization_id)
    return _order_to_response(refreshed)


async def create_order_for_retailer(
    db: AsyncSession, user: User, data: SupplierOrderCreateRequest
) -> OrderResponse:
    if user.role != UserRole.supplier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only suppliers can create manual orders",
        )

    from app.models.retailer import Retailer
    from sqlalchemy import select

    result = await db.execute(
        select(Retailer).where(
            Retailer.id == data.retailer_id,
            Retailer.organization_id == user.organization_id,
        )
    )
    retailer = result.scalar_one_or_none()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retailer not found in your organization",
        )

    subtotal = Decimal("0.00")
    tax = Decimal("0.00")
    product_cache = {}

    for item_req in data.items:
        product = await product_repo.get_product_by_id(
            db, item_req.product_id, user.organization_id
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_req.product_id} not found",
            )
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not active",
            )
        if product.stock < item_req.qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}",
            )
        product_cache[item_req.product_id] = product
        line_subtotal = product.price * item_req.qty
        line_tax = line_subtotal * product.gst_percent / Decimal("100")
        subtotal += line_subtotal
        tax += line_tax

    total = subtotal + tax

    order = await order_repo.create_order(
        db,
        organization_id=user.organization_id,
        retailer_id=retailer.id,
        status=OrderStatus.pending,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )

    for item_req in data.items:
        product = product_cache[item_req.product_id]
        await order_repo.create_order_item(
            db,
            order_id=order.id,
            product_id=item_req.product_id,
            qty=item_req.qty,
            price=product.price,
        )

    refreshed = await order_repo.get_order_by_id(db, order.id, user.organization_id)
    return _order_to_response(refreshed)


async def update_order_status(
    db: AsyncSession,
    order_id: uuid.UUID,
    user: User,
    data: OrderStatusUpdateRequest,
) -> OrderResponse:
    if user.role != UserRole.supplier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only suppliers can update order status",
        )

    order = await order_repo.get_order_by_id(db, order_id, user.organization_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if data.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{order.status.value}' to '{data.status.value}'. Allowed: {[s.value for s in allowed]}",
        )

    if data.status == OrderStatus.accepted:
        for item in order.items:
            product = await product_repo.get_product_by_id(
                db, item.product_id, user.organization_id
            )
            if not product or product.stock < item.qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {item.product_id}",
                )
            product.stock -= item.qty
        await db.flush()

    if data.status == OrderStatus.cancelled and order.status in (
        OrderStatus.accepted,
        OrderStatus.packed,
    ):
        for item in order.items:
            product = await product_repo.get_product_by_id(
                db, item.product_id, user.organization_id
            )
            if product:
                product.stock += item.qty
        await db.flush()

    order.status = data.status
    await db.flush()

    refreshed = await order_repo.get_order_by_id(db, order.id, user.organization_id)
    return _order_to_response(refreshed)


async def _get_retailer_for_user(db: AsyncSession, user: User):
    from app.models.retailer import Retailer
    from sqlalchemy import select

    result = await db.execute(
        select(Retailer).where(
            Retailer.user_id == user.id,
            Retailer.organization_id == user.organization_id,
        )
    )
    retailer = result.scalar_one_or_none()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retailer profile not found for this user",
        )
    return retailer
