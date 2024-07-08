from fastapi import APIRouter, Depends
from typing import List
from models import Customer, Regulars
from helpers import get_db_connection, fetch_and_map
from auth import AuthHandler

router = APIRouter(prefix="/api/customers")
auth_handler = AuthHandler()

@router.get("/", response_model=List[Customer])
def get_customers(db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = "SELECT * FROM Customers;"
    return fetch_and_map(db, query, Customer)


@router.get("/regular_customers/", response_model=List[Regulars])
def get_regular_customers(db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS orders_count
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        HAVING COUNT(o.order_id) >= 5
        ORDER BY orders_count DESC;
    """
    return fetch_and_map(db, query, Regulars)


@router.get("/{search_query}/", response_model=List[Customer])
def search_customers(search_query: str, db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT customer_id, first_name, last_name
        FROM Customers
        WHERE first_name LIKE %s OR last_name LIKE %s
    """
    like_term = f"%{search_query}%"
    return fetch_and_map(db, query, Customer, (like_term, like_term))
