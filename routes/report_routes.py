from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from models import ReportSummary
from helpers import get_db_connection, execute_query
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.get("/api/reports/", response_model=List[ReportSummary])
def get_reports(period: str = "day", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, 
                db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    if period not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Must be 'day', 'week', or 'month'.")

    if not start_date:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = datetime.now()

    query = """
        WITH OrderSummary AS (
            SELECT
                DATE(o.order_date) as order_day,
                YEARWEEK(o.order_date, 1) as order_week,
                DATE_FORMAT(o.order_date, '%Y-%m-01') as order_month,
                o.order_id,
                o.customer_id,
                SUM(oi.quantity * m.price) as order_total,
                m.name as item_name,
                SUM(oi.quantity) as item_quantity,
                CASE
                    WHEN %s = 'day' THEN DATE(o.order_date)
                    WHEN %s = 'week' THEN YEARWEEK(o.order_date, 1)
                    ELSE DATE_FORMAT(o.order_date, '%Y-%m-01')
                END as period_start
            FROM
                Orders o
                JOIN Order_Items oi ON o.order_id = oi.order_id
                JOIN Menu_Items m ON oi.item_id = m.item_id
            WHERE
                o.order_date BETWEEN %s AND %s
            GROUP BY
                o.order_id, m.item_id, order_day, order_week, order_month, o.customer_id, m.name, period_start
        ),
        TopItems AS (
            SELECT
                period_start,
                item_name,
                SUM(item_quantity) as total_quantity,
                ROW_NUMBER() OVER (
                    PARTITION BY period_start
                    ORDER BY SUM(item_quantity) DESC
                ) as rn
            FROM
                OrderSummary
            GROUP BY
                period_start, item_name
        )
        SELECT
            os.period_start,
            COUNT(DISTINCT os.order_id) as total_orders,
            COUNT(DISTINCT os.customer_id) as unique_customers,
            SUM(os.order_total) as total_revenue,
            AVG(os.order_total) as average_order_value,
            ti.item_name as top_selling_item,
            ti.total_quantity as top_selling_item_quantity
        FROM
            OrderSummary os
        JOIN
            TopItems ti ON os.period_start = ti.period_start AND ti.rn = 1
        GROUP BY
            os.period_start, ti.item_name, ti.total_quantity
        ORDER BY
            os.period_start;
    """

    results = execute_query(db, query, (period, period, start_date, end_date))

    summaries = []
    for row in results:
        period_start_str = row[0]

        if period == 'day':
            period_start = datetime.strptime(period_start_str, '%Y-%m-%d')
            period_end = period_start + timedelta(days=1)
        elif period == 'week':
            year_week_str = str(period_start_str)
            year = int(year_week_str[:4])
            week = int(year_week_str[4:])
            period_start = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
            period_end = period_start + timedelta(days=7)
        else:  # month
            period_start = datetime.strptime(period_start_str, '%Y-%m-01')
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = next_month - timedelta(days=next_month.day)

        summary = ReportSummary(
            period=period,
            start_date=period_start,
            end_date=period_end,
            total_orders=row[1],
            unique_customers=row[2],
            total_revenue=row[3],
            average_order_value=row[4],
            top_selling_item=row[5],
            top_selling_item_quantity=row[6]
        )
        summaries.append(summary)

    return summaries
