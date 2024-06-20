from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Menu(BaseModel):
    item_id: Optional[int] = None
    category: str
    name: str
    price: int

class OrderHistory(BaseModel):
    order_id: int
    order_date: datetime
    item: str
    quantity: int
    total_price: int

class Category(BaseModel):
    category_id: int
    name: str

class PopularMenuItems(BaseModel):
    item: str
    total_quantity: int

class Customer(BaseModel):
    customer_id: Optional[int] = None
    first_name: str
    last_name: str

class Regulars(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    orders_count: int

class OrderItem(BaseModel):
    item_id: int
    quantity: int

class Order(BaseModel):
    customer: Customer
    payment_method: str
    total_money: int
    items: List[OrderItem]
