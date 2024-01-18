"""
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
    Input model for data creation, so you can avoid passing back specific
    attributes, such as a password or a temporary field that assists creation.
    """
    pass


class ProductOutput(ProductBase):
    """
    Use this output model to include additional fields you want to return to
    the user, including fields that are generated after model creation
    (e.g, ID), or fields that are calculated, such as relationship fields.
    """
    product_id: int

    class Config:
        from_attributes = True  # for compatibility between models
