"""
Code for Chapter 10: Working With Data

Deleting Data.
"""
import logging

from models import Order, SessionMaker
from sqlalchemy import delete, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

DEBUG = False

if not DEBUG:
    logging.disable(logging.INFO)


# foreign key support for SQLite
# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


def delete_model_instance(session: Session):
    print("# Deleting ORM-mapped instance:")
    order = session.get(Order, 1)
    if order is not None:
        session.delete(order)
        print("Order in session after delete?", order in session)  # True
        session.commit()
        print("Order in session after committing?", order in session)  # False

    # check results
    for order in session.scalars(select(Order)):
        print(order)


def delete_using_where(session: Session):
    print("# Deleting remaining orders with WHERE:")
    stmt = delete(Order).where(Order.order_id != 1)
    session.execute(stmt)
    session.commit()

    # check results
    for order in session.scalars(select(Order)):
        print(order)


if __name__ == "__main__":
    with SessionMaker() as session:
        delete_model_instance(session)
        delete_using_where(session)
