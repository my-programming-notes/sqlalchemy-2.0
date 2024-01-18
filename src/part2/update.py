"""
Code for Chapter 10: Working With Data

Updating Data.
"""
import logging

from models import Customer, Product, SessionMaker
from sqlalchemy import select, update
from sqlalchemy.orm import Session

DEBUG = False

if not DEBUG:
    logging.disable(logging.INFO)


def update_using_model_attributes(session: Session):
    print("# ORM: updates using model attributes")

    mary = session.execute(
        select(Customer)
        .filter_by(first_name="Mary")
    ).scalar_one()

    print("Mary:", mary)

    mary.last_name = "Smith"
    print("Is instance modified:", session.is_modified(mary))
    print("Is object dirty:", mary in session.dirty)

    session.flush()
    print("Is instance modified after flushing:", session.is_modified(mary))
    print("Is object dirty after flushing:", mary in session.dirty)

    print("Mary updated:", mary)

    session.commit()


def update_using_where_clauses(session: Session):
    print("# ORM: updates using WHERE clauses and RETURNING")

    stmt = (
        update(Customer)
        .where(Customer.first_name.in_(["Alex", "Mary"]))
        .filter_by(last_name="Smith")
        .values(last_name="Taylor")
        .returning(Customer)
    )
    print("SQL:", stmt)
    customers = session.scalars(stmt)
    for customer in customers:
        print(customer)

    session.commit()


def update_bulk(session: Session):
    print("# ORM bulk update: restoring last names")

    session.execute(
        update(Customer),
        [
            {"customer_id": 1, "last_name": "Smith"},
            {"customer_id": 2, "last_name": "Taylor"},
        ],
    )
    session.commit()


def update_product_units_in_stock(session: Session):
    print("# Update using class attribute:")
    product = session.get(Product, 1)
    if product is not None:
        product.units_in_stock = Product.units_in_stock + 1
        session.commit()

    print("# Update using instance attribute:")
    product = session.get(Product, 1)
    if product is not None:
        product.units_in_stock -= 1
        session.commit()


if __name__ == "__main__":
    with SessionMaker() as session:
        # updating last names:
        update_using_model_attributes(session)
        update_using_where_clauses(session)
        update_bulk(session)

        # updates using class and instance Attributes
        update_product_units_in_stock(session)
