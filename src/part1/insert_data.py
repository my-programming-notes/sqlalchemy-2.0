"""
Code for Chapter 4: Creating Data.
"""
from datetime import date, timedelta

from sqlalchemy import Connection, insert
from sqlalchemy.exc import IntegrityError
from tables import (ProductType, customer, employee, engine, order,
                    order_detail, product)


def create_employees(conn: Connection):
    """
    Input employee data.
    """
    employee_ids = []

    # create the first manager Alice:
    stmt = (
        insert(employee)
        .values(
            name="Alice",
            is_manager=True,
            hire_date=(date.today() - timedelta(days=1)),
        )
    )

    # print the SQL statement and its parameters:
    print("SQL:", stmt)
    compiled = stmt.compile()
    print('params:', compiled.params)

    # execute it
    result = conn.execute(stmt)

    # the primary key of the manager just created is a tuple, hence "[0]"
    manager_alice_id = result.inserted_primary_key[0]
    print("Manager Alice PK:", manager_alice_id)
    employee_ids.append(manager_alice_id)

    conn.commit()  # commit as you go

    # insert many employees at once:
    result = conn.execute(
        (
            insert(employee)
            # if database supports RETURNING, we don't need to
            # query the database again for these info
            .returning(
                employee.c.employee_id,
                employee.c.name,
                employee.c.hire_date,
            )
        ),
        [
            {"manager_id": manager_alice_id, "name": "Bob"},
            {"manager_id": manager_alice_id, "name": "Cathy"},
        ],
    )

    # keys: ['employee_id', 'name', 'hire_date']
    print("keys:", list(result.keys()))

    for row in result:
        print(row)  # (employee_id, name, hire_date)
        # employee_ids.append(row[0])  # 0: employee_id
        employee_ids.append(row.employee_id)  # 0: employee_id

    conn.commit()  # commit as you go

    # create a second manager and a second employee
    result = conn.execute(
        insert(employee)
        .values(
            name="Louis",
            is_manager=True,
            hire_date=(date.today() - timedelta(days=30)),
        )
    )
    manager_louis_id = result.inserted_primary_key[0]
    employee_ids.append(manager_louis_id)

    result = conn.execute(
        insert(employee)
        .values(
            name="Lilly",
            manager_id=manager_louis_id,
            hire_date=(date.today() - timedelta(days=20)),
        )
    )
    employee_ids.append(result.inserted_primary_key[0])

    conn.commit()  # commit as you go

    # let's add another "Alice" (who is not a manager)
    conn.execute(
        insert(employee).values(
            name="Alice",
        )
    )
    conn.commit()  # commit as you go

    return employee_ids


def create_products(conn: Connection, product_data: list[dict]):
    """
    Product data for our online store.
    """
    product_ids = []

    result = conn.execute(
        insert(product).returning(
            # c: collection of table columns
            product.c.product_id, product.c.product_name
        ),
        product_data,
    )

    for row in result:
        print(row)  # (product_id, product_name)
        product_ids.append(row[0])

    conn.commit()

    return product_ids


def create_customers(conn: Connection, customer_data: list[dict]):
    """
    Customer data.
    """
    customer_ids = []
    try:
        result = conn.execute(
            (
                insert(customer)
                .returning(
                    customer.c.customer_id,
                    customer.c.first_name,
                )
            ),
            customer_data
        )
        for row in result:
            print(row)  # row contains tuples of (customer_id, first_name)
            customer_ids.append(row[0])
    except IntegrityError as e:
        print("Error creating customers!", e)

    conn.commit()

    return customer_ids


def place_orders(conn: Connection, customer_ids, product_ids):
    """
    Create orders and order details.
    """
    # customer and product IDs from previous return values:
    c1, c2 = customer_ids
    p1, p2, p3, p4, p5 = product_ids

    order_ids = []

    # first customer places 1st order
    result = conn.execute(insert(order).values(customer_id=c1))
    order1_id = result.inserted_primary_key[0]
    order_ids.append(order1_id)
    result = conn.execute(
        insert(order_detail),
        [
            # phone
            {"order_id": order1_id, "product_id": p1, "quantity": 1},
            # phone screen protector
            {"order_id": order1_id, "product_id": p2, "quantity": 1},
            # headphone
            {"order_id": order1_id, "product_id": p3, "quantity": 1},
        ]
    )
    print("order_detail PKs:", result.inserted_primary_key_rows)
    conn.commit()  # commit as you go

    # first customer places 2nd order
    result = conn.execute(insert(order).values(customer_id=c1))
    order2_id = result.inserted_primary_key[0]
    order_ids.append(order2_id)
    conn.execute(
        insert(order_detail)
        .values(
            order_id=order2_id,
            product_id=p5,  # memory card
            quantity=1,
        )
    )
    conn.commit()  # commit as you go

    # second customer places order on camera related products
    result = conn.execute(insert(order).values(customer_id=c2))
    order3_id = result.inserted_primary_key[0]
    order_ids.append(order3_id)
    conn.execute(
        insert(order_detail),
        [
            # digital camera
            {"order_id": order3_id, "product_id": p4, "quantity": 1},
            # memory card (won't be enough for all!)
            {"order_id": order3_id, "product_id": p5, "quantity": 2},
        ]
    )
    conn.commit()  # commit as you go

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
            "email": "alex_smith@test.com",
        },
        {
            "first_name": "Mary",
            "last_name": "Taylor",
            "address": "200-139 Jefferson Street, NY",
            "email": "mary_taylor@test.com",
        },
    ]

    # separation of concerns: manage the connection independently
    with engine.connect() as conn:

        employee_ids = create_employees(conn)
        print("# Employees IDs:", employee_ids)

        product_ids = create_products(conn, PRODUCT_DATA)
        print("# Product IDs:", product_ids)

        customer_ids = create_customers(conn, CUSTOMER_DATA)
        print("# Customer IDs:", customer_ids)

        order_ids = place_orders(conn, customer_ids, product_ids)
        print("# Order IDs:", order_ids)
