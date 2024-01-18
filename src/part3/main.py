"""
Code for Chapter 15:
SQLAlchemy Integration with FastAPI.
"""
import crud
import schemas
from fastapi import Depends, FastAPI
from models import SessionMaker
from sqlalchemy.orm import Session

app = FastAPI()


# Dependency Injection
def get_session():
    with SessionMaker() as session:
        yield session


@app.get("/")
def root():
    return {"message": "Product API"}


@app.post("/products", status_code=201, response_model=schemas.ProductOutput)
def create_product(
    product: schemas.ProductInput,
    session: Session = Depends(get_session),
):
    return crud.create_product(session, product)


@app.get("/products/{product_id}", response_model=schemas.ProductOutput)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    return crud.get_product(session, product_id)


@app.get("/products", response_model=list[schemas.ProductOutput])
def get_products(
    page: int = 1,
    page_size: int = 3,
    order_by: str = "product_id",
    direction: str = "asc",
    session: Session = Depends(get_session),
):
    return crud.get_products(session, page, page_size, order_by, direction)
