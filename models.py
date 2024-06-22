from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Menu(BaseModel):
    item_id: Optional[int] = None
    category: str
    name: str
    price: float

class OrderHistory(BaseModel):
    order_id: int
    order_date: datetime
    item: str
    quantity: int
    total_price: float

class Category(BaseModel):
    category_id: Optional[int] = None
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
    total_money: float
    items: List[OrderItem]

class ReportSummary(BaseModel):
    period: str
    start_date: datetime
    end_date: datetime
    total_orders: int
    unique_customers: int
    total_revenue: float
    average_order_value: float
    top_selling_item: str
    top_selling_item_quantity: int
