import os
from typing import List
from fastapi import FastAPI, Depends, Form, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datetime import datetime

import mysql.connector
from mysql.connector import Error

import config
from models import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


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
def get_popular_menu_items(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
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
def get_categories(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = "SELECT category_id, name FROM Categories;"
    return fetch_and_map(db, query, Category)


@app.get("/api/customers/", response_model=List[Customer])
def get_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = "SELECT * FROM Customers;"
    return fetch_and_map(db, query, Customer)


@app.get("/api/customers/search/", response_model=List[Customer])
def search_customers(search_query: str, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = """
        SELECT customer_id, first_name, last_name
        FROM Customers
        WHERE first_name LIKE %s OR last_name LIKE %s
    """
    like_term = f"%{search_query}%"
    return fetch_and_map(db, query, Customer, (like_term, like_term))


@app.get("/api/order_history/{client_id}", response_model=List[OrderHistory])
def get_order_history(client_id: int, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
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
def get_regular_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
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
def add_new_order(order: Order, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    try:
        if not order.customer.customer_id:
            query = "INSERT INTO Customers (first_name, last_name) VALUES (%s, %s)"
            customer_id = execute_insert(db, query, (order.customer.first_name, order.customer.last_name))
        else:
            customer_id = order.customer.customer_id

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
def add_new_item(items: List[Menu], db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    added_items = []
    try:
        for item in items:
            query = "SELECT category_id FROM Categories WHERE name = %s"
            category_result = execute_query(db, query, (item.category,))
            if not category_result:
                raise HTTPException(status_code=400, detail="Invalid category.")
            category_id = category_result[0]['category_id']

            query = "INSERT INTO Menu_Items (name, price, category_id) VALUES (%s, %s, %s)"
            item_id = execute_insert(db, query, (item.name, item.price, category_id))
            added_items.append(Menu(item_id=item_id, category=item.category, name=item.name, price=item.price))

        return added_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding new item: {str(e)}")


@app.post("/api/categories/", response_model=Category)
def add_category(category: Category, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    query = "INSERT INTO Categories (name) VALUES (%s)"
    category_id = execute_insert(db, query, (category.name,))
    return Category(category_id=category_id, name=category.name)


@app.post("/api/upload_image/")
async def upload_image(item_id: int, file: UploadFile = File(...)):
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


@app.get("/dashboard/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name=f"dashboard.html")


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/test/", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")