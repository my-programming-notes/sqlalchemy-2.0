"""
Code for Chapter 3: Schema and Types.
"""
import enum
from datetime import date, datetime

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, Enum,
                        ForeignKey, Index, Integer, MetaData, Numeric, String,
                        Table, create_engine)

# DATABASE_URL = "sqlite+pysqlite:///store.db"
DATABASE_URL = "postgresql+psycopg2://postgres:pw2023@localhost:5432/test"

metadata = MetaData()

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


employee = Table(
    "employee",
    metadata,
    Column("employee_id", Integer, primary_key=True),
    Column(
        "manager_id",
        Integer,
        ForeignKey("employee.employee_id"),
        nullable=True
    ),
    Column("name", String(31), nullable=False),
    Column("is_manager", Boolean, default=False),
    Column('hire_date', Date, default=date.today),
)


class ProductType(enum.Enum):
    PHONE = 0
    ACCESSORY = 1
    OTHER = 2


product = Table(
    "product",
    metadata,
    Column("product_id", Integer, primary_key=True),
    Column("product_name", String(255), index=True),
    Column(
        "unit_price",
        Numeric(12, 2),
        CheckConstraint("unit_price>0"),
    ),
    Column(
        "units_in_stock",
        Integer,
        CheckConstraint("units_in_stock>=0"),
        default=0,
    ),
    Column("type", Enum(ProductType), default=ProductType.OTHER),
)
# CheckConstraint(
#     product.c.units_in_stock < 1_000_000,
#     name="stock_upper_limit",
# )

customer = Table(
    "customer",
    metadata,
    Column("customer_id", Integer, primary_key=True),
    Column("first_name", String(31)),
    Column("last_name", String(31)),
    Column("address", String(255)),
    Column("email", String(127), unique=True, nullable=False),
)
# compound index for customer table:
Index("customer_full_name", customer.c.first_name, customer.c.last_name)


order = Table(
    "order",
    metadata,
    Column("order_id", Integer, primary_key=True),
    Column(
        "customer_id",
        Integer,
        ForeignKey("customer.customer_id"),
        nullable=False,
    ),
    Column(
        "employee_id",
        Integer,
        ForeignKey("employee.employee_id"),
        nullable=True,
    ),
    Column("order_datetime", DateTime, default=datetime.now),
    Column("is_shipped", Boolean, default=False),
)

order_detail = Table(
    "order_detail",
    metadata,
    Column(
        "order_id",
        Integer,
        ForeignKey("order.order_id"),
        primary_key=True,
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("product.product_id"),
        primary_key=True,
    ),
    Column("quantity", Integer,  default=1),
    CheckConstraint("quantity>0", name="num_of_ordered_item_must_be_positive"),
)


if __name__ == "__main__":
    # drop and recreate all tables:
    metadata.drop_all(engine)
    metadata.create_all(engine)
