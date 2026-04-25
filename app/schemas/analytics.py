from decimal import Decimal

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_retailers: int
    total_products: int
    total_orders: int
    total_revenue: Decimal
    pending_orders: int
    delivered_orders: int


class RevenueResponse(BaseModel):
    total_revenue: Decimal
    total_tax: Decimal
    total_orders: int


class TopProductItem(BaseModel):
    product_id: str
    product_name: str
    total_qty: int
    total_revenue: Decimal


class TopProductsResponse(BaseModel):
    items: list[TopProductItem]


class TopRetailerItem(BaseModel):
    retailer_id: str
    shop_name: str
    total_orders: int
    total_spent: Decimal


class TopRetailersResponse(BaseModel):
    items: list[TopRetailerItem]
