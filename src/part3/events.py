"""
Code for Chapter 14: Events
"""
import logging

from models import Customer, Product, ProductType, SessionMaker, engine
from sqlalchemy import select
from sqlalchemy.event import listen, listens_for
from sqlalchemy.orm import Session

# logger settings
logger = logging.getLogger("sqlalchemy_events")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()  # you can also define a file handler
formatter = logging.Formatter(
    "%(asctime)s [%(name)s][%(levelname)s] [%(funcName)s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def db_on_connect1(dbapi_connection, connection_record):
    logger.debug(f"Connected 1: {dbapi_connection}")


# register a listener with the `listen()` function
listen(engine, "connect", db_on_connect1)


# register a listener with the `listens_for()` decorator
@listens_for(engine, "connect")
def db_on_connect2(dbapi_connection, connection_record):
    logger.debug(f"Connected 2: {dbapi_connection}")


def list_products(session: Session):
    """List all products."""
    products = session.scalars(select(Product))
    print("Listing products...")
    for product in products:
        print(product)


# @listens_for(Product, 'before_insert')
# @listens_for(Product, 'before_update')
# def before_insert_update(mapper, connection, target: Product):
#     """MapperEvents.before_insert(), MapperEvents.before_update()"""
#     logger.debug(f"Input product name: {target.product_name}")
#     # converting product name to title case
#     target.product_name = target.product_name.title()


def insert_product(session: Session, data):
    product = Product(**data)
    session.add(product)
    session.commit()

    return product.product_id


def update_product(session: Session, product_id: int, new_product_name: str):
    product = session.get(Product, product_id)
    if product is not None:
        product.product_name = new_product_name
        session.commit()


def insert_customer(session: Session, data):
    customer = Customer(**data)
    session.add(customer)
    session.commit()

    return customer.customer_id


if __name__ == "__main__":

    product_data = {
        "product_name": "phone screen protector",
        "unit_price": 9.50,
        "units_in_stock": 10,
        "type": ProductType.ACCESSORY,
    }

    customer_data = {
        "first_name": "Alex",
        "last_name": "Smith",
        "address": "618 Oak Lane, CA",
        "email": "alex_smith@test.com",
    }

    with SessionMaker() as session:
        print(">> Session starts!")
        list_products(session)
        print(">> Session ends!")

        print("Inserting product...")
        product_id = insert_product(session, product_data)
        print("New product added:", session.get(Product, product_id))

        print("Updating product...")
        update_product(session, product_id, "phone screen protector 2023")
        print("Product updated to:", session.get(Product, product_id))

        product_id_2 = insert_product(session, product_data)
        print("New product added:", session.get(Product, product_id_2))

        customer_id = insert_customer(session, customer_data)
        print("Customer inserted:", session.get(Customer, customer_id))

        try:
            customer_data["email"] = "not_valid"
            customer_id = insert_customer(session, customer_data)
        except ValueError as e:
            print("A value error occurred:", e)
