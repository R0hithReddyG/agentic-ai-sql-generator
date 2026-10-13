from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from database.engine import get_engine
from database.models import (
    Base,
    Customer,
    Department,
    Employee,
    Order,
    OrderItem,
    Product,
)


def create_tables() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)


def seed_database() -> None:
    create_tables()
    engine = get_engine()
    with Session(engine) as session:
        if session.query(Department).count() > 0:
            return

        departments = [
            Department(department_name="Engineering", location="New York", budget=5000000),
            Department(department_name="Sales", location="Chicago", budget=3000000),
            Department(department_name="Marketing", location="San Francisco", budget=2000000),
            Department(department_name="HR", location="New York", budget=1000000),
            Department(department_name="Finance", location="Boston", budget=1500000),
        ]
        session.add_all(departments)
        session.flush()

        titles = ["Engineer", "Manager", "Analyst", "Director", "Specialist", "Lead"]
        employees = []
        for i in range(50):
            dept = random.choice(departments)
            emp = Employee(
                first_name=f"First{i}",
                last_name=f"Last{i}",
                email=f"emp{i}@company.com",
                department_id=dept.department_id,
                hire_date=date(2018, 1, 1) + timedelta(days=random.randint(0, 2000)),
                salary=float(random.randint(50000, 150000)),
                job_title=random.choice(titles),
            )
            employees.append(emp)
        session.add_all(employees)
        session.flush()

        customers = []
        cities = ["New York", "London", "Tokyo", "Berlin", "Sydney", "Toronto", "Mumbai"]
        countries = ["USA", "UK", "Japan", "Germany", "Australia", "Canada", "India"]
        for i in range(100):
            c_idx = random.randint(0, len(cities) - 1)
            cust = Customer(
                customer_name=f"Customer_{i}",
                email=f"customer{i}@example.com",
                phone=f"+1-555-{random.randint(1000,9999)}",
                city=cities[c_idx],
                country=countries[c_idx],
                registration_date=date(2020, 1, 1) + timedelta(days=random.randint(0, 1500)),
            )
            customers.append(cust)
        session.add_all(customers)
        session.flush()

        categories = ["Electronics", "Clothing", "Food", "Books", "Software", "Hardware"]
        products = []
        for i in range(30):
            prod = Product(
                product_name=f"Product_{i}",
                category=random.choice(categories),
                price=round(random.uniform(10.0, 1000.0), 2),
                stock_quantity=random.randint(0, 500),
            )
            products.append(prod)
        session.add_all(products)
        session.flush()

        statuses = ["pending", "shipped", "delivered", "cancelled"]
        orders = []
        for i in range(200):
            cust = random.choice(customers)
            emp = random.choice(employees)
            ord_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 730))
            order = Order(
                customer_id=cust.customer_id,
                employee_id=emp.employee_id,
                order_date=ord_date,
                total_amount=0.0,
                status=random.choice(statuses),
            )
            orders.append(order)
        session.add_all(orders)
        session.flush()

        for order in orders:
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            total = 0.0
            for prod in selected_products:
                qty = random.randint(1, 10)
                discount = round(random.uniform(0, 0.2), 2)
                unit_price = prod.price
                item_total = qty * unit_price * (1 - discount)
                total += item_total
                item = OrderItem(
                    order_id=order.order_id,
                    product_id=prod.product_id,
                    quantity=qty,
                    unit_price=unit_price,
                    discount=discount,
                )
                session.add(item)
            order.total_amount = round(total, 2)

        session.commit()
