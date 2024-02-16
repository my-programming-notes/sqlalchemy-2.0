"""
Code for Chapter 10: Working With Data

Inserting data.
"""
import logging
from datetime import date, timedelta

from models import (Customer, Employee, Order, OrderDetail, Product,
                    ProductType, SessionMaker)
from sqlalchemy import insert
from sqlalchemy.orm import Session

DEBUG = False

if not DEBUG:
    logging.disable(logging.INFO)


class DatabaseInitialization:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_employees(self):

        session = self.session

        # Alice and her two subordinates Bob and Cathy
        alice = Employee(
            name="Alice",
            is_manager=True,
            hire_date=date.today() - timedelta(days=1),
        )
        session.add(alice)
        bob = Employee(name="Bob")
        cathy = Employee(name="Cathy")
        # bob and cathy are added to the session via alice
        alice.employees.extend([bob, cathy])
        session.flush()  # flush to generate the PKs

        # Louis and his subordinate Lilly
        louis = Employee(
            name="Louis",
            is_manager=True,
            hire_date=date.today() - timedelta(days=30),
        )
        session.add(louis)
        lilly = Employee(
            name="Lilly",
            hire_date=date.today() - timedelta(days=20),
        )
        # use the manager relationship
        lilly.manager = louis
        session.add(lilly)
        session.flush()  # generate PKs

        # employee Alice
        alice2 = Employee(name="Alice")
        session.add(alice2)

        session.commit()

        # return employee IDs (compare with Core)
        return [
            alice.employee_id,
            bob.employee_id,
            cathy.employee_id,
            louis.employee_id,
            lilly.employee_id,
            alice2.employee_id,
        ]

    def create_products(self, product_data):
        if len(product_data) != 5:
            raise ValueError("There must be exactly 5 products!")

        session = self.session

        product_ids = []
        # can be done in a similar way to Core (bulk insert)
        products = session.scalars(
            insert(Product).returning(
                Product,
                # to ensure the order (might impact performance)
                sort_by_parameter_order=True,
            ),
            product_data
        )
        for product in products:
            print(product)
            product_ids.append(product.product_id)
        session.commit()

        return product_ids

    def create_customers(self, customer_data):
        if len(customer_data) != 2:
            raise ValueError("There should be exactly 2 customers!")

        session = self.session

        customer_ids = []
        # create customers one-by-one
        for data in customer_data:
            customer = Customer(**data)
            session.add(customer)
            session.flush()  # to generate PKs in order
            customer_ids.append(customer.customer_id)
        session.commit()

        return customer_ids

    def place_orders(self, customer_ids: list[int], product_ids: list[int]):
        session = self.session

        if (len(customer_ids) != 2) or (len(product_ids) != 5):
            raise ValueError("The array length of IDs is not correct!")

        # customer PKs:
        alex_id, mary_id = customer_ids

        # product PKs:
        (
            phone_id,
            screen_protector_id,
            headphone_id,
            camera_id,
            memory_card_id,
        ) = product_ids

        # array to save order IDs:
        order_ids = []

        # Alex's first order:
        order1 = Order(customer_id=alex_id)
        order1.order_details.extend([
            OrderDetail(product_id=phone_id),
            OrderDetail(product_id=screen_protector_id),
            OrderDetail(product_id=headphone_id),
        ])
        session.add(order1)

        session.flush()
        order_ids.append(order1.order_id)

        # Alex's second order:
        order2 = Order(customer_id=alex_id)
        OrderDetail(product_id=memory_card_id).order = order2
        session.add(order2)

        session.flush()
        order_ids.append(order2.order_id)

        # Mary's first order, or the third order:
        order3 = Order(customer_id=mary_id)
        session.add(order3)
        session.flush()  # flush to generate PK
        od31 = OrderDetail(product_id=camera_id, order_id=order3.order_id)
        od32 = OrderDetail(
            product_id=memory_card_id,
            order_id=order3.order_id,
            quantity=2,
        )
        session.add_all([od31, od32])

        session.commit()
        order_ids.append(order3.order_id)

        return order_ids


if __name__ == "__main__":

    PRODUCT_DATA = [
        {
            "product_name": "phone",
            "unit_price": 300.0,
            "units_in_stock": 5,
            "type": ProductType.PHONE,
        },
        {
            "product_name": "phone screen protector",
            "unit_price": 9.50,
            "units_in_stock": 10,
            "type": ProductType.ACCESSORY,
        },
        {
            "product_name": "headphone",
            "unit_price": 25.99,
            "units_in_stock": 10,
            "type": ProductType.ACCESSORY,
        },
        {
            "product_name": "digital camera",
            "unit_price": 45.99,
            "units_in_stock": 5,
            "type": ProductType.OTHER,
        },
        {
            "product_name": "memory card 256GB",
            "unit_price": 21.99,
            "units_in_stock": 1,
            "type": ProductType.ACCESSORY,
        },
    ]

    CUSTOMER_DATA = [
        {
            "first_name": "Alex",
            "last_name": "Smith",
            "address": "618 Oak Lane, CA",
            "email": "alex_smith@test.com"
        },
        {
            "first_name": "Mary",
            "last_name": "Taylor",
            "address": "200-139 Jefferson Street, NY",
            "email": "mary_taylor@test.com"
        },
    ]

    # manage the session independently (separation of concerns)
    with SessionMaker() as session:
        init_db = DatabaseInitialization(session)

        employee_ids = init_db.create_employees()
        print("# Employees IDs:", employee_ids)

        product_ids = init_db.create_products(PRODUCT_DATA)
        print("# Product IDs:", product_ids)

        customer_ids = init_db.create_customers(CUSTOMER_DATA)
        print("# Customer IDs:", customer_ids)

        order_ids = init_db.place_orders(customer_ids, product_ids)
        print("# Order IDs:", order_ids)
