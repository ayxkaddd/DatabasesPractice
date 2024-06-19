import os
from typing import List
from fastapi import FastAPI, Depends, Form, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


@app.get("/api/menu_items/", response_model=List[Menu])
def get_menu_items(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    menu_items = []
    cursor = db.cursor()
    cursor.execute("""
        SELECT m.item_id, c.name AS category, m.name AS item, m.price
        FROM Menu_Items m
        JOIN Categories c ON m.category_id = c.category_id
        ORDER BY c.name, m.name;
    """)
    rows = cursor.fetchall()
    for row in rows:
        menu_item = Menu(item_id=row[0], category=row[1], name=row[2], price=row[3])
        menu_items.append(menu_item)
    cursor.close()
    db.close()
    return menu_items


@app.get("/api/popular_menu_items/", response_model=List[PopularMenuItems])
def get_popular_menu_items(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    popular_menu_items = []
    cursor = db.cursor()
    cursor.execute("""
        SELECT m.name AS item, SUM(oi.quantity) AS total_quantity
        FROM Order_Items oi
        JOIN Menu_Items m ON oi.item_id = m.item_id
        GROUP BY m.name
        ORDER BY total_quantity DESC
        LIMIT 5;
    """)
    rows = cursor.fetchall()
    for row in rows:
        popular_menu_item = PopularMenuItems(item=row[0], total_quantity=row[1])
        popular_menu_items.append(popular_menu_item)

    cursor.close()
    db.close()
    return popular_menu_items


@app.get("/api/categories/", response_model=List[Category])
def get_categories(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    categories = []
    cursor = db.cursor()
    cursor.execute("SELECT category_id, name FROM Categories;")
    rows = cursor.fetchall()
    for row in rows:
        category = Category(category_id=row[0], name=row[1])
        categories.append(category)
    cursor.close()
    db.close()
    return categories


@app.get("/api/customers/", response_model=List[Customer])
def get_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    customers = []
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Customers;")
    rows = cursor.fetchall()
    for row in rows:
        customer = Customer(customer_id=row[0], first_name=row[1], last_name=row[2], email=row[3])
        customers.append(customer)
    cursor.close()
    db.close()
    return customers


@app.get("/api/order_history/{client_id}", response_model=List[OrderHistory])
def get_order_history(client_id: int, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    orders = []
    cursor = db.cursor()
    query = """
        SELECT o.order_id, o.order_date,
               GROUP_CONCAT(m.name ORDER BY m.name SEPARATOR ', ') AS items,
               SUM(oi.quantity) AS total_quantity,
               SUM(oi.quantity * m.price) AS total_price
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Menu_Items m ON oi.item_id = m.item_id
        WHERE o.customer_id = %s
        GROUP BY o.order_id, o.order_date
        ORDER BY o.order_date;
    """
    cursor.execute(query, (client_id,))
    rows = cursor.fetchall()
    for row in rows:
        history = OrderHistory(order_id=row[0], order_date=row[1], item=row[2], quantity=row[3], total_price=row[4])
        orders.append(history)
    cursor.close()
    db.close()
    return orders


@app.get("/api/regular_customers/", response_model=List[Regulars])
def get_regular_customers(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    regular_customers = []
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.customer_id, c.first_name, c.last_name, c.email, COUNT(o.order_id) AS orders_count
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name, c.email
        HAVING COUNT(o.order_id) >= 5
        ORDER BY orders_count DESC;
    """)
    rows = cursor.fetchall()
    for row in rows:
        regular_customer = Regulars(customer_id=row[0], first_name=row[1], last_name=row[2], email=row[3], orders_count=row[4])
        regular_customers.append(regular_customer)
    cursor.close()
    db.close()
    return regular_customers



@app.post("/api/add_new_item/", response_model=Menu)
def add_new_item(category: str = Form(...), name: str = Form(...), price: int = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category,))
        category_id = cursor.fetchone()
        if not category_id:
            raise HTTPException(status_code=400, detail="Invalid category.")

        cursor.execute("INSERT INTO Menu_Items (name, price, category_id) VALUES (%s, %s, %s)",
                       (name, price, category_id[0]))
        db.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        item_id = cursor.fetchone()[0]

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding new item: {str(e)}")
    finally:
        cursor.close()
        db.close()

    return Menu(item_id=item_id, category=category, name=name, price=price)


@app.post("/api/upload_image/")
async def upload_image(item_id: int, file: UploadFile = File(...)):
    allowed_extensions = {"jpg", "jpeg", "png"}

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    path = "static/images/"
    filename = os.path.join(path, f"{item_id}.jpg")
    if os.path.exists(filename):
        raise HTTPException(status_code=400, detail="File already exits.")

    try:
        contents = await file.read()
        with open(filename, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        file.file.close()

    return {"filename": file.filename}


@app.get("/dashboard/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name=f"dashboard.html")


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
