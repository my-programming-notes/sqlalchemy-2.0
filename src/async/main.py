"""
SQLAlchemy Integration with FastAPI.
"""
import crud
import schemas
from fastapi import Depends, FastAPI
from models import AsyncSessionMaker
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


# Dependency Injection
async def get_session() -> AsyncSession:
    async with AsyncSessionMaker() as session:
        yield session


@app.post("/products", status_code=201, response_model=schemas.ProductOutput)
async def create_product(
    product: schemas.ProductInput,
    session: AsyncSession = Depends(get_session),
):
    return await crud.create_product(session, product)


@app.get("/products/{product_id}", response_model=schemas.ProductOutput)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await crud.get_product(session, product_id)


@app.get("/products", response_model=list[schemas.ProductOutput])
async def get_products(
    page: int = 1,
    page_size: int = 3,
    order_by: str = "product_id",
    direction: str = "asc",
    session: AsyncSession = Depends(get_session),
):
    return await crud.get_products(session, page, page_size, order_by, direction)
