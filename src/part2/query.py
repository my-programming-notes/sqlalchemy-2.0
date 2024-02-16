"""
Code for Chapter 11: ORM API Features for Querying

Advanced query examples for ORM loader and execution options.
"""
import logging
import threading

from models import Customer, Employee, Order, OrderDetail, SessionMaker
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (Session, defer, load_only, selectinload, undefer,
                            undefer_group)

# turn on debugging to see lazy/relationship loading
DEBUG = True

if not DEBUG:
    logging.disable(logging.INFO)


def column_loading_options_load_only(session: Session):
    print("# load_only(): load only Employee name")
    stmt = (
        select(Employee)
        .filter_by(employee_id=1)
        .options(load_only(Employee.name))
    )
    print("# SQL:")
    print(stmt)

    employee = session.scalar(stmt)
    if employee is not None:
        print("# Accessing employee.hire_date (using lazy loading):")
        print(f"{employee.name} is hired on {employee.hire_date}.")


def column_loading_options_defer(session: Session):
    print("# defer(): defer loading individual Employee columns")
    stmt = (
        select(Employee)
        .filter_by(employee_id=1)
        .options(
            defer(Employee.hire_date),
            defer(Employee.manager_id),
            defer(Employee.is_manager),
        )
    )

    print("# SQL:")
    print(stmt)

    employee = session.scalar(stmt)
    if employee is not None:
        print("# Loading deferred column:")
        print(f"{employee.name} is hired on {employee.hire_date}.")


def column_loading_options_configured_on_mapping(session: Session):
    print("# Defer configured on Customer.address:")
    stmt = select(Customer)
    print(stmt)

    print("# Undefer Customer.address:")
    stmt = select(Customer).options(undefer(Customer.address))
    print(stmt)

    print("# Undefer group customer_attributes:")
    stmt = select(Customer).options(undefer_group("customer_attributes"))
    print(stmt)

    print("# Undefer using wildcard:")
    stmt = select(Customer).options(undefer("*"))
    print(stmt)


def column_loading_options_raiseload(session: Session):
    print("# Raiseload:")
    stmt = (
        select(Employee)
        .filter_by(employee_id=1)
        .options(load_only(Employee.name, raiseload=True))
    )

    employee = session.scalar(stmt)
    if employee is not None:
        print("Accessing employee name:", employee.name)

        try:
            print("Accessing other columns:", employee.hire_date)
        except SQLAlchemyError as e:
            print(e)


def relationship_loader_options(session: Session):

    def print_order_content(order: Order | None):
        """Common function to print the contents of an order."""
        if order is not None:
            print("# Accessing related data does not trigger lazy loading: ")
            print(f"Content of order #{order.order_id}:")
            for od in order.order_details:
                print(f"{od.product.product_name} x{od.quantity}")

    # This is probably the best way to eager load the relationships:
    # select IN for one-to-many, and joined loading for many-to-one
    print("# Select IN & Joined Loading:")
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_details)
            .joinedload(OrderDetail.product)
        )
        .filter_by(order_id=1)
    )
    order = session.scalar(stmt)
    print_order_content(order)


def n_plus_one_problem(session: Session):
    print("# N + 1 problem:")
    # the 1 part of the "N+1" problem
    customers = session.scalars(select(Customer))

    for customer in customers:
        print(f"> Customer: #{customer.customer_id}")
        for order in customer.orders:  # the N part of the "N+1" problem
            print(f">   order #{order.order_id} at {order.order_datetime}")


def n_plus_one_solved_with_selectin(session: Session):
    print("# N + 1 problem solved with select IN loading:")
    customers = session.scalars(
        select(Customer)
        .options(selectinload(Customer.orders))
    )
    for customer in customers:
        print(f"> Customer: #{customer.customer_id}")
        for order in customer.orders:
            print(f">   order #{order.order_id} at {order.order_datetime}")


def n_plus_one_solved_with_join(session: Session):
    print("# N + 1 problem solved by joining:")
    stmt = (
        select(
            Customer.customer_id,
            Order.order_id,
            Order.order_datetime,
        )
        .select_from(Customer)
        .join(Customer.orders)
        .order_by(Customer.customer_id, Order.order_id)
    )
    results = session.execute(stmt)

    current_customer_id = None
    for row in results:
        customer_id = row.customer_id
        if current_customer_id != customer_id:
            current_customer_id = customer_id
            print(f"> Customer: #{current_customer_id}")
        print(f">   order #{row.order_id} at {row.order_datetime}")


def execution_options_populate_existing(session: Session):
    print("# Execution options: populate existing")
    logging.disable(logging.INFO)

    TARGET_CUSTOMER_ID = 2

    stmt = (
        select(Customer)
        .where(Customer.customer_id == TARGET_CUSTOMER_ID)
        .options(selectinload(Customer.orders))
    )

    # initial loading populates the identity map
    print("(1) Initial loading:")
    customer = session.scalar(stmt)
    if customer is not None:
        print("Original:", customer.orders)

    def change_shipping_status(customer_id, status):
        with SessionMaker() as session:
            s1 = (
                select(Order.order_id)
                .where(Order.customer_id == customer_id)
                .order_by(Order.order_datetime)
                .limit(1)
            )
            order_id = session.scalar(s1)
            if order_id is not None:
                s2 = (
                    update(Order)
                    .where(Order.order_id == order_id)
                    .values(is_shipped=status)
                )
                session.execute(s2)
                session.commit()

    # change customer order's shipping status to true in another thread
    worker_thread = threading.Thread(
        target=change_shipping_status,
        args=(TARGET_CUSTOMER_ID, True),
    )
    worker_thread.start()
    worker_thread.join()

    # you can commit to get updates, but we're here for execution options
    # session.commit()

    # normal loading will not refresh the orders in the identity map
    print("(2) Normal loading after the update in another thread:")
    customer = session.scalar(stmt)
    if customer is not None:
        print("Updated but not refreshed:", customer.orders)

    # but with populate_existing, it reloads and you can see the changes
    print("(3) Loading with populate existing enabled:")
    stmt = stmt.execution_options(populate_existing=True)
    customer = session.scalar(stmt)
    if customer is not None:
        print("Updated and refreshed:", customer.orders)

    # restore shipping status
    change_shipping_status(TARGET_CUSTOMER_ID, False)


if __name__ == "__main__":
    with SessionMaker() as session:
        column_loading_options_load_only(session)
        column_loading_options_defer(session)
        column_loading_options_configured_on_mapping(session)
        column_loading_options_raiseload(session)

        relationship_loader_options(session)

        # N + 1 problem:
        n_plus_one_problem(session)
        n_plus_one_solved_with_selectin(session)
        n_plus_one_solved_with_join(session)

        execution_options_populate_existing(session)
