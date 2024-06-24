from fastapi import APIRouter, Depends
from typing import List
from models import Category
from helpers import get_db_connection, fetch_and_map, execute_insert
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.get("/api/categories/", response_model=List[Category])
def get_categories(db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = "SELECT category_id, name FROM Categories;"
    return fetch_and_map(db, query, Category)


@router.post("/api/categories/", response_model=Category)
def add_category(category: Category, db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = "INSERT INTO Categories (name) VALUES (%s)"
    category_id = execute_insert(db, query, (category.name,))
    return Category(category_id=category_id, name=category.name)