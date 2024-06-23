import os
import random
from typing import List
from fastapi import FastAPI, Depends, Form, HTTPException, Header, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datetime import datetime, timedelta

import mysql.connector
from mysql.connector import Error

import config
from auth import AuthHandler
from models import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

auth_handler = AuthHandler()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config.host,
            database='royal_praktyka',
            user=config.user,
            password=config.password
        )
        if connection.is_connected():
            return connection
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


def execute_query(db, query, params=None):
    cursor = db.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()


def execute_insert(db, query, params):
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()


def fetch_and_map(db, query, model_class, params=None):
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [model_class(**dict(zip(columns, row))) for row in cursor.fetchall()]
    finally:
        cursor.close()


@app.post('/api/login')
def login(auth_details: AuthDetails, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = """
    SELECT e.first_name, e.employee_id, e.employee_code, c.password
    FROM Employees e
    JOIN Credentials c ON e.employee_id = c.employee_id
    WHERE e.employee_code = %s
    """
    result = execute_query(db, query, (auth_details.employee_code,))

    if not result:
            raise HTTPException(status_code=401, detail="Invalid employee code")
    employee = result[0]
    print(result)
    print(employee[1])
    if not auth_handler.verify_password(auth_details.password, employee[3]):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(employee[0])
    return {'token': token}


@app.get("/api/employees/", response_model=List[Employee])
def get_employees(db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = "SELECT * FROM Employees;"
    return fetch_and_map(db, query, Employee)


@app.post('/api/employees/', status_code=201)
def create_employee(employee: Employee, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    if not employee.password:
        raise HTTPException(status_code=400, detail="Password is required")

    while True:
        employee_code = random.randint(1000, 9999)
        query = "SELECT COUNT(*) FROM Employees WHERE employee_code = %s"
        result = execute_query(db, query, (employee_code,))
        if result[0][0] == 0:
            break

    hashed_password = auth_handler.get_password_hash(employee.password)

    try:
        employee_query = """
        INSERT INTO Employees (first_name, last_name, employee_code)
        VALUES (%s, %s, %s)
        """
        employee_id = execute_insert(db, employee_query, (employee.first_name, employee.last_name, employee_code))

        credentials_query = """
        INSERT INTO Credentials (employee_id, password)
        VALUES (%s, %s)
        """
        execute_insert(db, credentials_query, (employee_id, hashed_password))
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/menu_items/", response_model=List[Menu])
def get_menu_items(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = """
        SELECT m.item_id, c.name AS category, m.name, m.price
        FROM Menu_Items m
        JOIN Categories c ON m.category_id = c.category_id
        ORDER BY c.name, m.name;
    """
    return fetch_and_map(db, query, Menu)


@app.get("/api/popular_menu_items/", response_model=List[PopularMenuItems])
def get_popular_menu_items(db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT m.name AS item, SUM(oi.quantity) AS total_quantity
        FROM Order_Items oi
        JOIN Menu_Items m ON oi.item_id = m.item_id
        GROUP BY m.name
        ORDER BY total_quantity DESC
        LIMIT 5;
    """
    return fetch_and_map(db, query, PopularMenuItems)


@app.get("/api/categories/", response_model=List[Category])
def get_categories(db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = "SELECT category_id, name FROM Categories;"
    return fetch_and_map(db, query, Category)


@app.get("/api/customers/", response_model=List[Customer])
def get_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = "SELECT * FROM Customers;"
    return fetch_and_map(db, query, Customer)


@app.get("/api/customers/{search_query}/", response_model=List[Customer])
def search_customers(search_query: str, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT customer_id, first_name, last_name
        FROM Customers
        WHERE first_name LIKE %s OR last_name LIKE %s
    """
    like_term = f"%{search_query}%"
    return fetch_and_map(db, query, Customer, (like_term, like_term))


@app.get("/api/order_history/{client_id}", response_model=List[OrderHistory])
def get_order_history(client_id: int, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT o.order_id, o.order_date,
               GROUP_CONCAT(m.name ORDER BY m.name SEPARATOR ', ') AS item,
               SUM(oi.quantity) AS quantity,
               SUM(oi.quantity * m.price) AS total_price
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Menu_Items m ON oi.item_id = m.item_id
        WHERE o.customer_id = %s
        GROUP BY o.order_id, o.order_date
        ORDER BY o.order_date;
    """
    return fetch_and_map(db, query, OrderHistory, (client_id,))


@app.get("/api/regular_customers/", response_model=List[Regulars])
def get_regular_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS orders_count
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        HAVING COUNT(o.order_id) >= 5
        ORDER BY orders_count DESC;
    """
    return fetch_and_map(db, query, Regulars)


@app.post("/api/order_add/", status_code=201)
def add_new_order(order: Order, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    try:
        customer_id = order.customer.customer_id
        if not customer_id:
            query = "INSERT INTO Customers (first_name, last_name) VALUES (%s, %s)"
            customer_id = execute_insert(db, query, (order.customer.first_name, order.customer.last_name))

        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO Orders (customer_id, order_date) VALUES (%s, %s)"
        order_id = execute_insert(db, query, (customer_id, order_date))

        for item in order.items:
            query = "INSERT INTO Order_Items (order_id, item_id, quantity) VALUES (%s, %s, %s)"
            execute_insert(db, query, (order_id, item.item_id, item.quantity))

        return {"message": "Order was successfully added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding new order: {str(e)}")


@app.post("/api/add_new_item/", response_model=List[Menu])
def add_new_item(items: List[Menu], db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    added_items = []
    try:
        for item in items:
            query = "SELECT category_id FROM Categories WHERE name = %s"
            category_result = execute_query(db, query, (item.category,))
            if not category_result:
                raise HTTPException(status_code=400, detail="Invalid category.")
            category_id = category_result[0][0]

            query = "INSERT INTO Menu_Items (name, price, category_id) VALUES (%s, %s, %s)"
            item_id = execute_insert(db, query, (item.name, item.price, category_id))
            added_items.append(Menu(item_id=item_id, category=item.category, name=item.name, price=item.price))

        return added_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding new item: {str(e)}")


@app.post("/api/categories/", response_model=Category)
def add_category(category: Category, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    query = "INSERT INTO Categories (name) VALUES (%s)"
    category_id = execute_insert(db, query, (category.name,))
    return Category(category_id=category_id, name=category.name)


@app.post("/api/upload_image/")
async def upload_image(item_id: int, file: UploadFile = File(...), token=Depends(auth_handler.auth_wrapper)):
    allowed_extensions = {"jpg", "jpeg", "png"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    path = "static/images/"
    filename = os.path.join(path, f"{item_id}.jpg")
    if os.path.exists(filename):
        raise HTTPException(status_code=400, detail="File already exists.")

    try:
        contents = await file.read()
        with open(filename, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        await file.close()

    return {"filename": file.filename}


@app.get("/api/reports/", response_model=List[ReportSummary])
def get_reports(period: str = "day", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: mysql.connector.MySQLConnection = Depends(get_db_connection), token=Depends(auth_handler.auth_wrapper)):
    if period not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Must be 'day', 'week', or 'month'.")

    if not start_date:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = datetime.now()

    query = """
        WITH OrderSummary AS (
            SELECT
                DATE(o.order_date) as order_day,
                YEARWEEK(o.order_date, 1) as order_week,
                DATE_FORMAT(o.order_date, '%Y-%m-01') as order_month,
                o.order_id,
                o.customer_id,
                SUM(oi.quantity * m.price) as order_total,
                m.name as item_name,
                SUM(oi.quantity) as item_quantity,
                CASE
                    WHEN %s = 'day' THEN DATE(o.order_date)
                    WHEN %s = 'week' THEN YEARWEEK(o.order_date, 1)
                    ELSE DATE_FORMAT(o.order_date, '%Y-%m-01')
                END as period_start
            FROM
                Orders o
                JOIN Order_Items oi ON o.order_id = oi.order_id
                JOIN Menu_Items m ON oi.item_id = m.item_id
            WHERE
                o.order_date BETWEEN %s AND %s
            GROUP BY
                o.order_id, m.item_id, order_day, order_week, order_month, o.customer_id, m.name, period_start
        ),
        TopItems AS (
            SELECT
                period_start,
                item_name,
                SUM(item_quantity) as total_quantity,
                ROW_NUMBER() OVER (
                    PARTITION BY period_start
                    ORDER BY SUM(item_quantity) DESC
                ) as rn
            FROM
                OrderSummary
            GROUP BY
                period_start, item_name
        )
        SELECT
            os.period_start,
            COUNT(DISTINCT os.order_id) as total_orders,
            COUNT(DISTINCT os.customer_id) as unique_customers,
            SUM(os.order_total) as total_revenue,
            AVG(os.order_total) as average_order_value,
            ti.item_name as top_selling_item,
            ti.total_quantity as top_selling_item_quantity
        FROM
            OrderSummary os
        JOIN
            TopItems ti ON os.period_start = ti.period_start AND ti.rn = 1
        GROUP BY
            os.period_start, ti.item_name, ti.total_quantity
        ORDER BY
            os.period_start;
    """

    results = execute_query(db, query, (period, period, start_date, end_date))

    summaries = []
    for row in results:
        period_start_str = row[0]

        if period == 'day':
            period_start = datetime.strptime(period_start_str, '%Y-%m-%d')
            period_end = period_start + timedelta(days=1)
        elif period == 'week':
            year_week_str = str(period_start_str)
            year = int(year_week_str[:4])
            week = int(year_week_str[4:])
            period_start = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
            period_end = period_start + timedelta(days=7)
        else:  # month
            period_start = datetime.strptime(period_start_str, '%Y-%m-01')
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = next_month - timedelta(days=next_month.day)

        summary = ReportSummary(
            period=period,
            start_date=period_start,
            end_date=period_end,
            total_orders=row[1],
            unique_customers=row[2],
            total_revenue=row[3],
            average_order_value=row[4],
            top_selling_item=row[5],
            top_selling_item_quantity=row[6]
        )
        summaries.append(summary)


    return summaries


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/test/", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")
