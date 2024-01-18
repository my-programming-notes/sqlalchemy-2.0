"""
Database CRUD operations for FastAPI service.
"""
import models
import schemas
from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_product(session: AsyncSession, product: schemas.ProductInput):
    db_product = models.Product(**product.model_dump())
    session.add(db_product)
    await session.commit()

    # test: try and comment out `expire_on_commit=False`
    print("product created:", db_product.product_id)

    return db_product


async def get_product(session: AsyncSession, product_id: int):
    product = await session.get(models.Product, product_id)
    if product is not None:
        # test: load relationship (lazy loading in async)
        orders = await product.awaitable_attrs.orders
        print("Orders should be empty:", orders)

        # you can NOT directly access orders
        # without explicitly loading it first
        # (try and comment out the above)
        print("product.orders:", product.orders)

    return product


async def get_products(
        session: AsyncSession,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
):
    stmt = (
        select(models.Product)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if direction == "asc":
        stmt = stmt.order_by(order_by)
    elif direction == "desc":
        stmt = stmt.order_by(desc(order_by))
    else:
        raise HTTPException(
            status_code=400,
            detail='Use asc or desc for the direction parameter.',
        )

    products = (await session.scalars(stmt)).all()

    return products
