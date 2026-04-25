import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import product as product_repo
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
    StockUpdateRequest,
)


async def list_products(
    db: AsyncSession, organization_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> ProductListResponse:
    products, total = await product_repo.get_products(
        db, organization_id, skip, limit
    )
    items = [ProductResponse.model_validate(p) for p in products]
    return ProductListResponse(items=items, total=total)


async def get_product(
    db: AsyncSession, product_id: uuid.UUID, organization_id: uuid.UUID
) -> ProductResponse:
    product = await product_repo.get_product_by_id(db, product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return ProductResponse.model_validate(product)


async def create_product(
    db: AsyncSession, organization_id: uuid.UUID, data: ProductCreateRequest
) -> ProductResponse:
    product = await product_repo.create_product(
        db,
        organization_id=organization_id,
        name=data.name,
        sku=data.sku,
        category=data.category,
        pic_url=data.pic_url,
        price=data.price,
        stock=data.stock,
        gst_percent=data.gst_percent,
        is_active=data.is_active,
    )
    return ProductResponse.model_validate(product)


async def update_product(
    db: AsyncSession,
    product_id: uuid.UUID,
    organization_id: uuid.UUID,
    data: ProductUpdateRequest,
) -> ProductResponse:
    product = await product_repo.get_product_by_id(db, product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    product = await product_repo.update_product(db, product, **update_data)
    return ProductResponse.model_validate(product)


async def delete_product(
    db: AsyncSession, product_id: uuid.UUID, organization_id: uuid.UUID
) -> dict:
    product = await product_repo.get_product_by_id(db, product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    product.is_active = False
    await db.flush()
    return {"message": "Product deactivated"}


async def update_stock(
    db: AsyncSession,
    product_id: uuid.UUID,
    organization_id: uuid.UUID,
    data: StockUpdateRequest,
) -> ProductResponse:
    product = await product_repo.get_product_by_id(db, product_id, organization_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    new_stock = product.stock + data.quantity
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Current: {product.stock}, requested change: {data.quantity}",
        )

    product.stock = new_stock
    await db.flush()
    return ProductResponse.model_validate(product)
