from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from models import Order, OrderHistory
from helpers import fetch_and_map, get_db_connection, execute_insert
from auth import AuthHandler

router = APIRouter(prefix="/api/orders")
auth_handler = AuthHandler()

@router.post("/add/", status_code=201)
def add_new_order(order: Order, db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
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


@router.get("/{client_id}", response_model=List[OrderHistory])
def get_order_history(client_id: int, db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
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
