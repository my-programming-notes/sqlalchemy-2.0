"""
Code for chapter 7: Reflection

To simulate individual programs, each function will manage its own connection.
"""
# DATABASE_URL = "sqlite+pysqlite:///store.db"
from sqlalchemy import MetaData, Table, create_engine, select, update

DATABASE_URL = "postgresql+psycopg2://postgres:pw2023@localhost:5432/test"


def reflect_single_product_table():
    metadata = MetaData()
    engine = create_engine(
        DATABASE_URL,
    )

    product = Table("product", metadata, autoload_with=engine)
    print("Product table columns:", [c.name for c in product.columns])
    print("Tables in metadata:", metadata.tables.keys())

    print("# Products:")
    with engine.connect() as conn:
        stmt = (
            select(product)
            .order_by(product.c.product_id)
        )
        for row in conn.execute(stmt):
            print(row)


def assign_order_to_employee():
    metadata = MetaData()
    engine = create_engine(
        DATABASE_URL,
    )

    order = Table("order", metadata, autoload_with=engine)
    # related tables (FK) are also loaded
    print("Tables in metadata:", [key for key in metadata.tables.keys()])
    print("Order table columns:", [c.name for c in order.columns])

    employee = metadata.tables["employee"]
    print("Employee table columns:", [c.name for c in employee.columns])

    # an problematic order is assigned to an employee
    with engine.connect() as conn:
        # find a suitable employee
        stmt1 = (
            select(employee.c.employee_id)
            .where(
                employee.c.is_manager == False,
                employee.c.manager_id != None,
            )
        )
        employee_id = conn.scalar(stmt1)
        print(f"Employee that should handle the issue: #{employee_id}")

        # find the problematic order (the 3rd order)
        # and assign it to the employee
        stmt2 = (
            select(order.c.order_id)
            .where(order.c.is_shipped == False)
        )
        order_id = conn.scalar(stmt2)
        print(f"The order with a problem: #{order_id}")

        # assign the order to the employee
        stmt3 = (
            update(order)
            .where(order.c.order_id == order_id)
            .values(employee_id=employee_id)
            .returning(order.c.order_id, order.c.employee_id)
        )
        updated_order = conn.execute(stmt3).first()
        print(
            f"Updated order: #{updated_order.order_id}, "
            f"assigned employee ID: #{updated_order.employee_id}."
        )

        conn.commit()


def reflect_all_tables():
    metadata = MetaData()
    engine = create_engine(
        DATABASE_URL,
    )

    metadata.reflect(bind=engine)
    print("Tables in metadata:", metadata.tables.keys())

    product = metadata.tables["product"]
    print("# Products:")
    with engine.connect() as conn:
        stmt = (
            select(product)
            .order_by(product.c.product_id)
        )
        for row in conn.execute(stmt):
            print(row)


def show_manager_view():
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
    metadata = MetaData()
    engine = create_engine(DATABASE_URL)

    manager_view = Table("manager", metadata, autoload_with=engine)
    print("manager_view columns:", [c.name for c in manager_view.columns])

    with engine.connect() as conn:
        stmt = (
            select(manager_view)
            .order_by(manager_view.c.id)
        )
        for row in conn.execute(stmt):
            print(row)


if __name__ == "__main__":

    print("# reflect_single_product_table()")
    reflect_single_product_table()

    print("# assign_order_to_employee():")
    assign_order_to_employee()

    print("# reflect_all_tables():")
    reflect_all_tables()

    # print("# show_manager_view():")
    # show_manager_view()
