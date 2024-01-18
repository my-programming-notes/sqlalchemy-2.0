"""
Code for Chapter 5: Reading Data.
"""
from typing import Sequence

from sqlalchemy import (Connection, Row, String, and_, asc, between, cast,
                        distinct, func, not_, or_, select, text)
from tables import (ProductType, customer, employee, engine, order,
                    order_detail, product)


def get_all_employees(conn: Connection):
    stmt = (
        select(employee)
    )
    print("SQL:", stmt)
    result = conn.execute(stmt)
    print("rowcount:", result.rowcount)

    return result.all()


def print_all_employee_names_and_hire_dates(conn: Connection):
    stmt = (
        select(employee.c.name, employee.c.hire_date)
    )
    print("SQL:", stmt)

    result = conn.execute(stmt)
    for row in result:
        print(row)


def print_all_employee_names_and_hire_dates_ordered_by_date(conn: Connection):
    stmt = (
        select(employee.c.name, employee.c.hire_date)
        .order_by(asc(employee.c.hire_date))
        # .order_by(employee.c.hire_date.asc())
    )
    print("SQL:", stmt)

    result = conn.execute(stmt)
    for row in result:
        print(row)


def print_limited_results(
        conn: Connection,
        num: int = 3,
):
    stmt = (
        select(employee.c.name, employee.c.hire_date)
        .order_by(employee.c.hire_date.asc())
        .limit(num)
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    result = conn.execute(stmt)
    for row in result:
        print(row)


def print_labeled_columns(conn: Connection):
    stmt = (
        select(
            employee.c.name,
            ("hire date: " + cast(employee.c.hire_date, String))
            .label("hired_on")
        )
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    result = conn.execute(stmt)
    print("keys:", result.keys())
    for row in result:
        print(f"{row.name:>5}, {row.hired_on}")


def get_all_managers(conn: Connection):
    stmt = (
        select(employee)
        .where(employee.c.is_manager == True)
    )
    print("SQL:", stmt)
    result = conn.execute(stmt)

    return result.all()


def get_manager_alice(conn: Connection):
    stmt = (
        select(
            employee
        )
        # .where(employee.c.is_manager == True)
        # .where(employee.c.name == "Alice")
        .where(
            employee.c.is_manager == True,
            employee.c.name == "Alice",
        )
    )
    print("SQL:", stmt)
    result = conn.execute(stmt)

    return result.first()


def get_manager_alice_with_and_(conn: Connection):
    stmt = (
        select(employee)
        .where(
            and_(employee.c.is_manager == True,
                 employee.c.name == "Alice",)
        )
    )
    result = conn.execute(stmt)

    return result.first()


def get_all_managers_named_alice_and_louis(conn: Connection):
    stmt = (
        select(employee)
        .where(
            and_(
                employee.c.is_manager == True,
                or_(
                    employee.c.name == "Alice",
                    employee.c.name == "Louis",
                )
            )
        )
    )
    print("SQL:", stmt)
    result = conn.execute(stmt)

    return result.all()


def get_all_non_alice_managers(conn: Connection):
    stmt = (
        select(employee)
        .where(
            and_(
                employee.c.is_manager == True,
                not_(employee.c.name == "Alice"),
            )
        )
    )
    print("SQL:", stmt)
    result = conn.execute(stmt)

    return result.all()


def get_all_alices(conn: Connection):
    stmt = (
        select(employee)
        .where(
            employee.c.name == "Alice"
        )
    )
    result = conn.execute(stmt)

    return result.all()


def print_products_between_a_price_range(
        conn: Connection,
        lower: int = 10,
        upper: int = 100,
):
    stmt = (
        select(
            product.c.product_name,
            product.c.unit_price,
        )
        .where(
            # product.c.unit_price.between(lower, upper)
            between(product.c.unit_price, lower, upper)
        )
    )
    result = conn.execute(stmt)
    for row in result:
        print(f"{row[0]:<18}: ${float(row[1])}")


def get_distinct_names(conn: Connection):
    stmt = (
        # select(distinct(employee.c.name))
        select(employee.c.name.distinct())
        .order_by(employee.c.name)
    )
    print("SQL:", stmt)
    result = conn.scalars(stmt)

    return result.all()


def print_all_phones_and_accessories(conn: Connection):
    # define columns in a separate array:
    columns = [product.c.product_name, product.c.type]

    stmt = (
        select(*columns)
        .where(
            product.c.type.in_(
                [ProductType.PHONE, ProductType.ACCESSORY]
            )
        )
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)

    for row in conn.execute(stmt):
        print(f"{(row[1].name):<9}: {row.product_name}")


def print_all_products_like_phone(conn: Connection):
    stmt = (
        select(product.c.product_name)
        .where(product.c.product_name.ilike("%phone%"))
    )
    print("SQL:", stmt)
    print("params:", stmt.compile().params)
    for product_name in conn.scalars(stmt):
        print(product_name)


def print_order_content(conn: Connection, order_id):
    columns = [
        product.c.product_name,
        product.c.unit_price,
        order_detail.c.quantity,
        order.c.order_datetime,
    ]

    # 1st way to construct the query
    # stmt = (
    #     select(*columns)
    #     .select_from(order_detail)
    #     .join(order)
    #     .join(product)
    #     .where(order.c.order_id == order_id)
    # )

    # 2nd way to construct the query
    # stmt = (
    #     select(*columns)
    #     .join_from(order, order_detail)
    #     .join_from(order_detail, product)
    #     .where(order.c.order_id == order_id)
    # )

    # explicit ON clauses
    stmt = (
        select(*columns)
        .select_from(order_detail)
        .join(order, order_detail.c.order_id == order.c.order_id)
        .join(product, order_detail.c.product_id == product.c.product_id)
        .where(order.c.order_id == order_id)
    )

    print("SQL:", stmt)

    result = conn.execute(stmt)
    for row in result:
        print(
            f'{row.order_datetime.strftime("%Y-%m-%d %H:%M:%S")} '
            f'{row.product_name:<22}: '
            f'{row.unit_price:>7} *{row.quantity}'
        )


def print_all_employees_with_manager(conn: Connection):
    # alias for employee table
    manager = employee.alias("manager")

    columns = [
        employee.c.employee_id,
        employee.c.name,
        manager.c.name.label("manager"),
        manager.c.employee_id.label("manager_id"),
    ]

    stmt = (
        select(*columns)
        .select_from(employee)
        .join(
            manager,
            employee.c.manager_id == manager.c.employee_id,
            isouter=True,
        )
    )
    print("SQL:", stmt)

    result = conn.execute(stmt)
    for row in result:
        if row.manager is not None:
            print(f"{row.name}({row.employee_id})'s manager is "
                  f"{row.manager}({row.manager_id}).")
        else:
            print(f"{row.name}({row.employee_id}) has no manager.")


def count_employees(conn: Connection):
    stmt = (
        select(func.count())
        .select_from(employee)
    )
    print("SQL:", stmt)

    count = conn.scalar(stmt)
    print(f"We have {count} employees.")


def cost_of_the_most_expensive_product(conn: Connection):
    stmt = (
        select(func.max(product.c.unit_price))
    )
    print("SQL:", stmt)

    max_price = conn.scalar(stmt)
    print(f"The most expensive product costs ${max_price}.")


def list_all_managers_with_employee_count(
        conn: Connection,
        max_subordinates=4,
):
    manager = employee.alias("manager")
    stmt = (
        select(
            manager.c.name,
            func.count(employee.c.employee_id).label("count"),
        )
        .join(employee, employee.c.manager_id == manager.c.employee_id)
        .group_by(manager.c.employee_id)
        .having(func.count(employee.c.employee_id) < max_subordinates)
        .order_by(func.count(employee.c.employee_id))
    )
    print("SQL:", stmt)

    result = conn.execute(stmt)
    for row in result:
        print(f"{row.name}: {row.count}")


def raw_query(conn: Connection):
    t = text("SELECT customer_id, first_name FROM customer")
    print("TextClause:", t)

    result = conn.execute(t)
    for row in result:
        print(row.customer_id, row.first_name)


def raw_query_with_bound_param(conn: Connection, customer_id: int):
    # t = (
    #     text(
    #         "SELECT customer_id, first_name "
    #         "FROM customer "
    #         "WHERE customer_id=:id"
    #     )
    #     .bindparams(id=customer_id)
    # )

    # partial raw queries:
    t = (
        select(customer.c.customer_id, customer.c.first_name)
        .where(
            text("customer_id=:id")
            .bindparams(id=customer_id)
        )
    )
    print("SQL:", t)
    result = conn.execute(t).first()
    print(result)


def get_orders_for_customers(
        conn: Connection,
        name: str | None = None,
        is_shipped: bool = False,
        details: bool = True
) -> Sequence[Row]:
    print(f"> Params: name={name}, is_shipped={is_shipped}, details={details}")

    # put columns in an individual array, so we can extend it later
    columns = [
        customer.c.first_name,
        customer.c.last_name,
        order.c.order_id,
        order.c.is_shipped,
    ]
    # these two tables are always needed, so join them first
    joined = customer.join(order)

    # if details are required, more columns and tables are incorporated
    if details:
        columns.extend([
            product.c.product_name,
            order_detail.c.quantity,
            product.c.unit_price,
        ])
        joined = joined.join(order_detail).join(product)

    # the rows are filtered by the shipping status
    stmt = (
        select(*columns)
        .select_from(joined)
        .where(order.c.is_shipped == is_shipped)
    )

    # and also filtered by first name
    if name is not None:
        stmt = stmt.where(customer.c.first_name == name)

    # print("SQL:", stmt)

    result = conn.execute(stmt)

    return result.all()


def print_orders_for_customers(orders: Sequence[Row]) -> None:
    order_id = None
    for row in orders:
        current_order_id = row.order_id
        if order_id is None or order_id != current_order_id:
            order_id = current_order_id
            print(f"{row.first_name} {row.last_name} "
                  f"has an order with ID:{current_order_id}")
        if hasattr(row, "product_name"):
            print(f"- {row.product_name}: ${row.unit_price} *{row.quantity}")


if __name__ == "__main__":
    with engine.connect() as conn:
        print("# get_all_employees():")
        employees = get_all_employees(conn)
        for e in employees:
            print(e)

        print("# print_all_employee_names_and_hire_dates():")
        print_all_employee_names_and_hire_dates(conn)

        print("# print_all_employee_names_and_hire_dates_ordered_by_date():")
        print_all_employee_names_and_hire_dates_ordered_by_date(conn)

        print("# print_limited_results():")
        print_limited_results(conn, 3)

        print("# print_labeled_columns():")
        print_labeled_columns(conn)

        print("# get_all_managers():")
        managers = get_all_managers(conn)
        for m in managers:
            print(m)

        print("# get_manager_alice():")
        alice = get_manager_alice(conn)
        print(alice)

        print("# get_manager_alice_with_and_():")
        alice = get_manager_alice_with_and_(conn)
        print(alice)

        print("# get_all_managers_named_alice_and_louis():")
        alice_and_louis = get_all_managers_named_alice_and_louis(conn)
        for m in managers:
            print(m)

        print("# get_all_non_alice_managers():")
        non_alice_managers = get_all_non_alice_managers(conn)
        for m in non_alice_managers:
            print(m)

        print("# get_all_alices():")
        alices = get_all_alices(conn)
        for alice in alices:
            print(alice)

        print("# print_products_between_a_price_range():")
        print_products_between_a_price_range(conn)

        print("# get_distinct_names():")
        names = get_distinct_names(conn)
        for name in names:
            print(name)

        print("# print_all_phones_and_accessories():")
        print_all_phones_and_accessories(conn)

        print("# print_all_products_like_phone():")
        print_all_products_like_phone(conn)

        print("# print_order_content():")
        print_order_content(conn, 1)

        print("# print_all_employees_with_manager():")
        print_all_employees_with_manager(conn)

        print("# count_employees():")
        count_employees(conn)

        print("# cost_of_the_most_expensive_product():")
        cost_of_the_most_expensive_product(conn)

        print("# list_all_managers_with_employee_count():")
        print("# default limit:")
        list_all_managers_with_employee_count(conn)
        print("# limit = 2:")
        list_all_managers_with_employee_count(conn, 2)

        print("# raw_query():")
        raw_query(conn)

        print("# raw_query_with_bound_param():")
        raw_query_with_bound_param(conn, 1)

        print("# get_orders_for_customers():")
        orders = get_orders_for_customers(
            conn, None, is_shipped=False, details=True,
        )
        print_orders_for_customers(orders)

        orders = get_orders_for_customers(
            conn, "Alex", is_shipped=False, details=True,
        )
        print_orders_for_customers(orders)

        orders = get_orders_for_customers(
            conn, "Alex", is_shipped=False, details=False,
        )
        print_orders_for_customers(orders)

        orders = get_orders_for_customers(
            conn, "Alex", is_shipped=True, details=False,
        )
        print_orders_for_customers(orders)
