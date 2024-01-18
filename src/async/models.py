from __future__ import annotations  # PEP-563

import datetime
import enum
import re
from decimal import Decimal
from typing import Annotated

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass,
                            mapped_column, query_expression, relationship,
                            validates)

# use asyncpg
DATABASE_URL = "postgresql+asyncpg://postgres:pw2023@localhost:5432/test"

# use create_async_engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# async_sessionmaker: a factory for new AsyncSession objects.
# expire_on_commit - don't expire objects after transaction commit
AsyncSessionMaker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class ProductType(enum.Enum):
    """
    The enumeration for our product types.
    Products are divided into: phone, accessory, and other types.
    """
    PHONE = 0
    ACCESSORY = 1
    OTHER = 2


# AsyncAttrs: to "await" for lazy loaded attributes
class Base(AsyncAttrs, MappedAsDataclass,  DeclarativeBase):
    """
    Declarative base with Python dataclass integration.
    """
    pass


# Define re-usable types:
int_pk = Annotated[
    int,
    mapped_column(
        primary_key=True,
    )
]
date_auto = Annotated[
    datetime.date,
    mapped_column(
        default=datetime.date.today,
    )
]
timestamp_auto = Annotated[
    datetime.datetime,
    mapped_column(
        default=datetime.datetime.now,
    ),
]
str_127 = Annotated[
    str,
    mapped_column(
        String(127),
    )
]
str_255 = Annotated[
    str,
    mapped_column(
        String(255),
    )
]
num_12_2 = Annotated[
    Decimal,
    mapped_column(
        Numeric(12, 2),
    )
]


class Employee(Base):
    __tablename__ = "employee"

    employee_id: Mapped[int_pk] = mapped_column(init=False)

    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.employee_id"),
        default=None,
    )

    first_name: Mapped[str_127] = mapped_column(
        CheckConstraint(
            "length(name)>0",
            name="name_length_must_be_at_least_one_character",
        ),
        default="",
    )
    last_name: Mapped[str_127 | None] = mapped_column(
        default="",
    )

    is_manager: Mapped[bool] = mapped_column(default=False)
    hire_date: Mapped[date_auto] = mapped_column(default=None)

    # self-referential relationship: manager/employees
    manager: Mapped[Employee] = relationship(
        back_populates="employees",
        remote_side=[employee_id],
        init=False,
        repr=False,
    )
    employees: Mapped[list[Employee]] = relationship(
        back_populates="manager",
        init=False,
        repr=False,
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="employee",
        init=False,
        repr=False,
    )


class Customer(Base):
    __tablename__ = "customer"

    customer_id: Mapped[int_pk] = mapped_column(init=False)

    first_name: Mapped[str_127]
    last_name: Mapped[str_127]
    # deferred attributes needs to be loaded eagerly in async
    address: Mapped[str_255] = mapped_column(
        deferred=True,
        deferred_group="customer_attributes",
    )
    email: Mapped[str_127] = mapped_column(unique=True)

    order_count: Mapped[int] = query_expression(repr=False)

    __table_args__ = (
        Index("customer_full_name", "first_name", "last_name"),
    )

    # same with lazily loaded relationships, you can use:
    # `await customer.awaitable_attrs.orders`
    orders: Mapped[list[Order]] = relationship(
        lazy="select",
        back_populates="customer",
        init=False,
        repr=False,
        order_by="desc(Order.order_id)",
    )

    @validates("email")
    def validate_email(self, key, value):
        if not is_email_valid(value):
            raise ValueError("Email validation failed!")
        return value


def is_email_valid(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    else:
        return False


class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[int_pk] = mapped_column(init=False)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.customer_id"),
        default=None,
    )
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.employee_id"),
        default=None,
    )

    order_datetime: Mapped[timestamp_auto] = mapped_column(init=False)
    is_shipped: Mapped[bool] = mapped_column(default=False)

    customer: Mapped[Customer] = relationship(
        back_populates="orders",
        init=False,
        repr=False,
    )
    employee: Mapped[Employee | None] = relationship(
        back_populates="orders",
        init=False,
        repr=False,
    )

    # relationship with associative table:
    order_details: Mapped[list[OrderDetail]] = relationship(
        back_populates="order",
        init=False,
        repr=False,
        # cascade: "all" implies "refresh-expire", avoid using it with asyncio
        cascade="save-update, merge, expunge, delete, delete-orphan",
        passive_deletes=True,
    )

    # many-to-many relationship with `Product`, bypassing `OrderDetail` class
    products: Mapped[list[Product]] = relationship(
        init=False,
        repr=False,
        secondary="order_detail",
        back_populates="orders",
        viewonly=True,  # avoid conflicting changes between relations
    )

    product_names: AssociationProxy[list[str]] = association_proxy(
        "products",
        "product_name",
        init=False,
        repr=False,
    )


class OrderDetail(Base):
    """
    Association object pattern.
    This uses the associative table between Order and Product.
    """
    __tablename__ = "order_detail"

    order_id: Mapped[int] = mapped_column(
        # database side: ON DELETE CASCADE
        ForeignKey("order.order_id", ondelete="CASCADE"),
        primary_key=True,
        default=None,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.product_id"),
        primary_key=True,
        default=None,
    )

    quantity: Mapped[int] = mapped_column(
        CheckConstraint(
            "quantity>0",
            name="num_of_ordered_item_must_be_positive",
        ),
        default=1,
    )

    order: Mapped[Order] = relationship(
        back_populates="order_details",
        init=False,
        repr=False,
    )

    product: Mapped[Product] = relationship(
        back_populates="order_details",
        init=False,
        repr=False,
    )


class Product(Base, repr=False):  # type: ignore
    __tablename__ = "product"

    product_id: Mapped[int_pk] = mapped_column(init=False)

    product_name: Mapped[str_255] = mapped_column(index=True)
    unit_price: Mapped[num_12_2] = mapped_column(
        CheckConstraint("unit_price>0"))
    units_in_stock: Mapped[int] = mapped_column(
        CheckConstraint("units_in_stock>=0"),
        default=0,
    )
    type: Mapped[ProductType] = mapped_column(
        default=ProductType.OTHER,
    )

    order_details: Mapped[list[OrderDetail]] = relationship(
        init=False,
        repr=False,
        back_populates="product",
    )

    # many-to-many relationship to `Order`, bypassing `OrderDetail`
    orders: Mapped[list[Order]] = relationship(
        init=False,
        secondary="order_detail",
        back_populates="products",
        viewonly=True,
    )

    # customize repr:
    def __repr__(self) -> str:
        return (
            "Product("
            f"product_id={self.product_id}, "
            f"product_name='{self.product_name}', "
            f"unit_price={self.unit_price}, "
            f"units_in_stock={self.units_in_stock}, "
            f"type='{self.type.name.lower()}'"
            ")"
        )

    @validates("product_name")
    def validate_product_name(self, key, value: str):
        return value.title()
