"""
Code for Chapter 15:
Pydantic models for FastAPI.
"""
from decimal import Decimal

from models import ProductType
from pydantic import BaseModel


class ProductBase(BaseModel):
    """
    Common base model for creating and reading data.
    """
    product_name: str
    unit_price: Decimal
    units_in_stock: int = 0
    type: ProductType = ProductType.OTHER


class ProductInput(ProductBase):
    """
    Input model for data creation. The separation of input and output models
    helps prevent the inclusion of unwanted attributes, like passwords or
    temporary fields used during creation, from being transmitted back in the
    output.
    """
    pass


class ProductOutput(ProductBase):
    """
    Use this output model to include additional fields you want to return to
    the user, including fields that are generated after model creation
    (e.g., PK) or fields that are calculated, such as relationship fields.
    """
    product_id: int

    class Config:
        from_attributes = True  # for compatibility between models
