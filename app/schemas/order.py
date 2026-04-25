import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemRequest(BaseModel):
    product_id: uuid.UUID
    qty: int = Field(..., gt=0)


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest] = Field(..., min_length=1)


class SupplierOrderCreateRequest(BaseModel):
    retailer_id: uuid.UUID
    items: list[OrderItemRequest] = Field(..., min_length=1)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    qty: int
    price: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    retailer_id: uuid.UUID
    retailer_name: str = ""
    retailer_phone: str = ""
    retailer_address: str = ""
    status: OrderStatus
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
