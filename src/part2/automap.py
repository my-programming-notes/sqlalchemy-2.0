"""
Code for Chapter 12: Reflection with the ORM `Automap` Extension
"""
import logging
import re

import inflect  # pip install inflect
from models import SessionMaker, engine
from sqlalchemy import Column, Integer, Table, select
from sqlalchemy.ext.automap import AutomapBase, automap_base
from sqlalchemy.orm import Session

DEBUG = False

if not DEBUG:
    logging.disable(logging.INFO)


def camelize_classname(base, tablename, table):
    """
    Produce a 'camelized' class name, e.g.,
    'words_and_underscores' is transformed into 'WordsAndUnderscores'.
    """
    return str(tablename[0].upper() +
               re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))


_pluralizer = inflect.engine()


def pluralize_collection(base, local_cls, referred_cls, constraint):
    """
    Produce an 'uncamelized', 'pluralized' class name, e.g.,
    'SomeTerm' becomes 'some_terms'.
    """
    referred_name = referred_cls.__name__
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         referred_name)[1:]
    pluralized = _pluralizer.plural(uncamelized)
    return pluralized


def automap_default(session: Session):
    print("# Automap default:")
    Base: AutomapBase = automap_base()
    Base.prepare(autoload_with=engine)  # reflect database
    print("Classes reflected:", Base.classes.keys())

    Order = Base.classes.order

    # print the content of an order
    order = session.scalars(select(Order).filter_by(order_id=1)).one()
    print(f"# Order: #{order.order_id}")
    # collection-based relationships are
    # by default named "<classname>_collection"
    for order_detail in order.order_detail_collection:
        quantity = order_detail.quantity
        product_name = order_detail.product.product_name
        print(f"{product_name} x{quantity}")


def automap_custom(session: Session):
    print("# Automap with custom naming rules:")
    Base: AutomapBase = automap_base()
    Base.prepare(
        autoload_with=engine,
        classname_for_table=camelize_classname,
        name_for_collection_relationship=pluralize_collection
    )
    print("Classes reflected:", Base.classes.keys())

    # repeat the previous example with naming customization:
    order = session.scalars(
        select(Base.classes.Order).filter_by(order_id=1)
    ).one()
    print(f"# Order: #{order.order_id}")
    for order_detail in order.order_details:
        quantity = order_detail.quantity
        product_name = order_detail.product.product_name
        print(f"{product_name} x{quantity}")


def automap_view(session: Session):
    """
    First, create a view with SQL:

    CREATE VIEW manager AS
    SELECT
        employee_id AS id,
        "name",
        hire_date
    FROM
        employee e
    WHERE
        e.is_manager = TRUE;

    """
    print("# Reflecting a view with automap:")
    Base: AutomapBase = automap_base()

    # add table (view) to metadata:
    Table(
        "manager",
        Base.metadata,
        # PK is required for reflection to work
        Column('id', Integer, primary_key=True),
        autoload_with=engine,
    )
    Base.prepare(
        # autoload_with=engine,  # to load all tables
        classname_for_table=camelize_classname,
        name_for_collection_relationship=pluralize_collection
    )
    print("Classes reflected:", Base.classes.keys())

    Manager = Base.classes.Manager
    print("Listing managers:")
    with Session(engine) as session:
        for manager in session.scalars(select(Manager)):
            print(manager.id, manager.name, manager.hire_date)


if __name__ == "__main__":
    with SessionMaker() as session:
        automap_default(session)
        automap_custom(session)
        automap_view(session)
