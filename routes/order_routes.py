from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from models import Order
from helpers import get_db_connection, execute_insert
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.post("/api/order_add/", status_code=201)
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
