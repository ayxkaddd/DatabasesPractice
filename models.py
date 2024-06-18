from pydantic import BaseModel
from datetime import datetime

class Menu(BaseModel):
    item_id: int
    category: str
    name: str
    price: int


class OrderHistory(BaseModel):
    order_id: int
    order_date: datetime
    item: str
    quantity: int
    total_price: int


class PopularMenuItems(BaseModel):
    item: str
    total_quantity: int


class Regulars(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    orders_count: int


class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
