"""
For Chapter 10: Working With Data

Reading Data.
"""

import logging

from models import (Customer, Employee, Order, OrderDetail, Product,
                    ProductType, SessionMaker)
from sqlalchemy import and_, asc, desc, not_, or_, select, text, union_all
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, aliased, selectinload
from sqlalchemy.sql.functions import count

DEBUG = False

if not DEBUG:
    logging.disable(logging.INFO)


def select_products(session: Session):
    """Comparing `Session.execute()` vs. `Session.scalars()`."""
    stmt = select(Product)

    print("# Session.execute():")
    for row in session.execute(stmt):
        print(row)

    print("# Session.scalars():")
    for product in session.scalars(stmt):
        print(product)


def products_result_methods(session: Session):
    """Result methods: all, first, scalar, scalars."""
    stmt = select(Product)

    result = session.execute(stmt)
    print("# Result.all():")
    print(result.all())

    result = session.execute(stmt)
    print("# Result.first():")
    print(result.first())

    result = session.execute(stmt)
    print("# Result.scalar():")
    print(result.scalar())

    products = session.execute(stmt).scalars()
    print("# products:")
    print(products.all())

    products = session.execute(stmt).scalars()
    print("# first product:")
    print(products.first())

    try:
        print("# one():")
        session.execute(stmt).one()
    except Exception as e:
        print(e)

    try:
        print("# one_or_none():")
        session.execute(stmt).one_or_none()
    except Exception as e:
        print(e)


def product_specific_columns(session: Session):

    def execute_stmt(stmt):
        for row in session.execute(stmt):
            print(f"{row.product_name:<22}: ${row.unit_price}")

    print("# Product name and price:")
    stmt = select(Product.product_name, Product.unit_price)
    execute_stmt(stmt)

    print("# Ordered by price (high to low):")
    stmt = stmt.order_by(Product.unit_price.desc())
    execute_stmt(stmt)

    print("# Offset and limiting (page size = 2, second page):")
    stmt = stmt.offset((2 - 1) * 2).limit(2)
    execute_stmt(stmt)


def product_filtering(session: Session):
    print("# Product filtering:")
    stmt = (
        select(Product.product_name)
        .where(Product.type == ProductType.PHONE)
    )
    print(session.scalars(stmt).all())

    stmt = (
        select(Product.product_name)
        .filter_by(type=ProductType.ACCESSORY)
    )
    print(session.scalars(stmt).all())

    stmt = (
        select(Product.product_name)
        .where(Product.type == ProductType.ACCESSORY)
        .where(Product.unit_price < 10)
    )
    print(session.scalars(stmt).all())


def manager_with_at_least_one_subordinate(session: Session):
    print("# Manager with at least one subordinate:")
    stmt = (
        select(Employee)
        .where(Employee.employees.any())
    )
    print(stmt)
    for employee in session.scalars(stmt):
        print(employee)


def conjunctions_using_and(session: Session):
    print("# Conjunctions: and_")
    stmt = (
        select(Product.product_name)
        .where(
            and_(
                Product.type == ProductType.ACCESSORY,
                Product.unit_price < 10,
            )
        )
    )
    print(session.scalars(stmt).all())


def conjunctions_using_or(session: Session):
    print("Conjunctions: or_")
    stmt = (
        select(Employee.employee_id, Employee.name)
        .where(
            or_(
                Employee.is_manager == True,
                Employee.manager != None,
            )
        )
    )
    for row in session.execute(stmt):
        print(row)


def show_order_details(session: Session, order_id: int):
    print("# select, join, join:")
    stmt = (
        select(Product.product_name, Product.unit_price, OrderDetail.quantity)
        .join(OrderDetail.product)
        .join(OrderDetail.order)
        .where(Order.order_id == order_id)
    )
    print("SQL:", stmt)
    for row in session.execute(stmt):
        print(row)

    print("# select_from, join, join:")
    stmt = (
        select(Product.product_name, Product.unit_price, OrderDetail.quantity)
        .select_from(Order)
        .join(Order.order_details)
        .join(OrderDetail.product)
        .where(Order.order_id == order_id)
    )
    print("SQL:", stmt)
    for row in session.execute(stmt):
        print(row)

    print("# join_from, join_from:")
    stmt = (
        select(Product.product_name, Product.unit_price, OrderDetail.quantity)
        .join_from(Order, OrderDetail)
        .join_from(OrderDetail, Product)
        .where(Order.order_id == order_id)
    )
    print("SQL:", stmt)
    for row in session.execute(stmt):
        print(row)


def employee_reports_to(session: Session):
    Manager = aliased(Employee, name="manager")
    stmt = (
        select(
            Employee.name,
            Employee.employee_id,
            Manager.name.label("manager"),
            Manager.employee_id.label("manager_id"),
        )
        .join(Manager, Employee.manager_id == Manager.employee_id)
        .where(Employee.manager_id != None)
    )
    print(stmt)
    for row in session.execute(stmt):
        print(
            f"{row.name}#{row.employee_id} "
            f"reports to {row.manager}#{row.manager_id}."
        )


def customer_orders_count(session: Session, min_count: int = 0):
    print("# Customer orders:")
    stmt = (
        select(
            Customer.first_name,
            Customer.last_name,
            count(Order.order_id).label("count"),
        )
        .join(Customer.orders)
        .group_by(Customer.customer_id)
        .having(count(Order.order_id) > min_count)
        .order_by(desc("count"))
    )
    print("SQL:", stmt)
    for row in session.execute(stmt):
        orders = "order" if (row.count == 1) else "orders"
        print(f"{row.first_name} {row.last_name} has {row.count} {orders}.")


def list_customer_orders(
        session: Session,
        name: str | None = None,
        is_shipped: bool = False,
        details: bool = True
):
    stmt = (
        select(
            Customer.first_name,
            Customer.last_name,
            Order.order_id,
            Order.is_shipped,
        )
        .join(Customer.orders)
        .where(Order.is_shipped == is_shipped)
    )

    if details:
        stmt = stmt.add_columns(
            Product.product_name,
            OrderDetail.quantity,
            Product.unit_price,
        ).join(Order.order_details).join(OrderDetail.product)

    if name is not None:
        stmt = stmt.where(Customer.first_name == name)

    for row in session.execute(stmt):
        print(row)


def raw_query(session: Session):
    print("# Raw query:")
    clause = text("SELECT customer_id, first_name FROM customer")
    for row in session.execute(clause):
        print(row.customer_id, row.first_name)


if __name__ == "__main__":
    with SessionMaker() as session:
        select_products(session)
        products_result_methods(session)
        product_specific_columns(session)
        product_filtering(session)
        manager_with_at_least_one_subordinate(session)
        conjunctions_using_and(session)
        conjunctions_using_or(session)

        # joins:
        show_order_details(session, 1)
        employee_reports_to(session)
        customer_orders_count(session)

        # conditional queries and chaining:
        print("# Orders for all customers that are not shipped, with details:")
        list_customer_orders(session, None, is_shipped=False, details=True)
        print("# Orders for Alex that are not shipped, with details:")
        list_customer_orders(
            session, "Alex", is_shipped=False, details=True)
        print("# Orders for Alex that are not shipped, without details:")
        list_customer_orders(
            session, "Alex", is_shipped=False, details=False)
        print("# Orders for Alex that are shipped, without details:")
        list_customer_orders(
            session, "Alex", is_shipped=True, details=False)

        raw_query(session)
