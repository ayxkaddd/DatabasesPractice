from fastapi import APIRouter, Depends, HTTPException
from typing import List
from mysql.connector import Error

from models import Menu, PopularMenuItems
from helpers import get_db_connection, fetch_and_map, execute_insert, execute_query
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.get("/api/menu_items/", response_model=List[Menu])
def get_menu_items(db=Depends(get_db_connection)):
    query = """
        SELECT m.item_id, c.name AS category, m.name, m.price
        FROM Menu_Items m
        JOIN Categories c ON m.category_id = c.category_id
        ORDER BY c.name, m.name;
    """
    return fetch_and_map(db, query, Menu)


@router.patch("/api/menu_items/")
async def update_menu_items(
    items: List[Menu], db = Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    cursor = db.cursor()
    try:
        for item in items:
            cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (item.category,))
            category_result = cursor.fetchone()
            if not category_result:
                raise HTTPException(status_code=400, detail=f"Category '{item.category}' not found")
            category_id = category_result[0]

            update_query = """
            UPDATE Menu_Items
            SET category_id = %s, name = %s, price = %s
            WHERE item_id = %s
            """
            cursor.execute(update_query, (category_id, item.name, item.price, item.item_id))

        db.commit()
        return {"message": f"Successfully updated {len(items)} menu items"}

    except Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor.close()


@router.get("/api/menu_items/popular/", response_model=List[PopularMenuItems])
def get_popular_menu_items(db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = """
        SELECT m.name AS item, SUM(oi.quantity) AS total_quantity
        FROM Order_Items oi
        JOIN Menu_Items m ON oi.item_id = m.item_id
        GROUP BY m.name
        ORDER BY total_quantity DESC
        LIMIT 5;
    """
    return fetch_and_map(db, query, PopularMenuItems)


@router.post("/api/menu_items/add/", response_model=List[Menu])
def add_new_item(items: List[Menu], db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
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
