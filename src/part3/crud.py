"""
Code for Chapter 15:
Database CRUD operations for FastAPI service.
"""
from fastapi import HTTPException
import models
import schemas
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


def create_product(session: Session, product: schemas.ProductInput):
    db_product = models.Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)  # not necessary, just in case

    return db_product


def get_product(session: Session, product_id: int):
    return session.get(models.Product, product_id)


def get_products(
        session: Session,
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

    products = session.scalars(stmt).all()

    return products
