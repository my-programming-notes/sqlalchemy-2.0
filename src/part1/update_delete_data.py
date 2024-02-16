"""
Code for Chapter 6: Updating and Deleting Data.
"""
from sqlalchemy import Connection, bindparam, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, StatementError
from tables import employee, engine, order, order_detail, product


def decrement_product(
        conn: Connection,
        product_id: int,
        quantity: int = 1,
):
    stmt = (
        update(product)
        .where(product.c.product_id == product_id)
        .values(units_in_stock=product.c.units_in_stock - quantity)
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    conn.execute(stmt)
    conn.commit()


def decrement_product_and_return(
    conn: Connection,
    product_id: int,
    quantity: int = 1,
):
    stmt = (
        update(product)
        .where(product.c.product_id == product_id)
        .values(units_in_stock=product.c.units_in_stock - quantity)
        .returning(product.c.product_name, product.c.units_in_stock)
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    result = conn.execute(stmt)
    decremented = result.first()
    conn.commit()

    return decremented


def restore_inventory(conn: Connection):
    stmt = (
        update(product)
        .where(product.c.product_id == bindparam("id"))
        .values(units_in_stock=bindparam("units"))
    )
    print("SQL:", stmt)

    result = conn.execute(
        stmt,
        [
            {"id": 1, "units": 5},
            {"id": 2, "units": 10},
            {"id": 3, "units": 10},
            {"id": 4, "units": 5},
            {"id": 5, "units": 1},
        ],
    )
    conn.commit()
    print(f"Matching rows: {result.rowcount}")


def update_exception(conn: Connection):
    stmt = update(product).values(units_in_stock=-1)
    conn.execute(stmt)


def process_order(conn: Connection, order_id: int):
    print(f"# Processing order {order_id}.")

    # check if the order is already processed
    stmt = (
        select(order.c.is_shipped)
        .where(order.c.order_id == order_id)
    )
    is_shipped = conn.scalar(stmt)
    if is_shipped:
        print("The order is already shipped.")
        return

    # order is not shipped, process it
    # get the order details: (product_id, quantity)
    stmt = (
        select(order_detail.c.product_id, order_detail.c.quantity)
        .where(order_detail.c.order_id == order_id)
    )
    result = conn.execute(stmt)

    # process each product ordered
    update_success = True
    for product_id, quantity in result:
        print(f"Processing product#{product_id} x{quantity}.")
        try:
            stmt_update = (
                update(product)
                .where(product.c.product_id == product_id)
                # you can also check for negative values
                .values(units_in_stock=product.c.units_in_stock - quantity)
            )
            conn.execute(stmt_update)
        except IntegrityError as e:
            print("An error occurred while updating product's units in stock!")
            print(e.orig)

            # to continue using the same connection for further operations,
            # roll back the current transaction
            print("Rolling back transaction...")
            conn.rollback()

            update_success = False
            break

    if update_success:
        stmt_update = (
            update(order)
            .where(order.c.order_id == order_id)
            .values(is_shipped=True)
        )
        conn.execute(stmt_update)

        # commit explicitly in commit-as-you-go
        conn.commit()


def print_order_and_product_status(conn: Connection):
    print("# Order status:")
    stmt = (
        select(order.c.order_id, order.c.is_shipped)
        .order_by(order.c.order_id)
    )
    for row in conn.execute(stmt):
        print(f"Order#{row.order_id}, shipped: {row.is_shipped}")

    print("# Product status:")
    stmt = (
        select(
            product.c.product_id,
            product.c.product_name,
            product.c.units_in_stock
        )
        .order_by(product.c.product_id)
    )
    for row in conn.execute(stmt):
        print(f"Product#{row[0]} {row[1]}: {row[2]}")


def delete_employee(conn: Connection, name: str):
    stmt = (
        delete(employee)
        .where(employee.c.name == name)
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    result = conn.execute(stmt)
    print("Employees selected for deletion:", result.rowcount)

    conn.commit()


def delete_employees_print_deleted(conn: Connection):
    stmt = (
        delete(employee)
        .where(
            employee.c.is_manager == False,
            employee.c.manager_id == None,
        )
        .returning(
            employee.c.employee_id,
            employee.c.name,
        )
    )

    result = conn.execute(stmt)
    print("Employees selected for deletion:", result.rowcount)
    for row in result:
        print(row)

    conn.commit()

# the following 2 functions use separate connections for style demonstration:


def transaction_commit_as_you_go():
    # commit as you go
    with engine.connect() as conn:

        stmt = insert(employee).values(name="Amelia")
        conn.execute(stmt)  # transaction 1 begins automatically
        conn.commit()  # transaction 1 committed, Amelia is hired!

        stmt = insert(employee).values(name="Brian")
        conn.execute(stmt)  # new transaction 2 begins
        conn.rollback()  # transaction 2 is rolled back

        stmt = insert(employee).values(name="Charlotte")
        conn.execute(stmt)  # another new transaction 3 begins
        conn.commit()  # transaction 3 committed, Charlotte is hired!


def transaction_begin_once():
    with engine.begin() as conn:
        stmt = insert(employee).values(name="Daniel")
        conn.execute(stmt)
        stmt = insert(employee).values(name="Emily")
        conn.execute(stmt)
        # the transaction is committed implicitly at the end of this block


if __name__ == "__main__":

    # these use a separate connection for demonstrating the styles
    print("# transaction_commit_as_you_go():")
    transaction_commit_as_you_go()
    print("# transaction_begin_once():")
    transaction_begin_once()

    with engine.connect() as conn:
        print("# decrement_product():")
        decrement_product(conn, 4)  # camera ID = 4

        print("# decrement_product_and_return():")
        decremented_product = decrement_product_and_return(conn, 4)
        print(decremented_product)

        print("# restore_inventory():")
        restore_inventory(conn)

        try:
            print("# update_exception():")
            update_exception(conn)
        except SQLAlchemyError as e:
            print(f"Some {type(e).__name__} occurred!")
            print(e)

            if isinstance(e, StatementError):
                print("Error extends from StatementError, listing attributes:")
                print("statement:", e.statement)
                print("params:", e.params)
                print("orig:", e.orig)

            conn.rollback()  # necessary to reuse the same connection

        print("# process_order():")
        process_order(conn, 1)
        process_order(conn, 2)
        process_order(conn, 3)

        print("# print_order_and_product_status():")
        print_order_and_product_status(conn)

        print("# delete_employee():")
        delete_employee(conn, "Amelia")

        print("# delete_employees_print_deleted():")
        delete_employees_print_deleted(conn)
