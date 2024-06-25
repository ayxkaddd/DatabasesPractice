from fastapi import HTTPException
import mysql.connector
from mysql.connector import Error

import config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password
        )
        if connection.is_connected():
            return connection
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


def execute_query(db, query, params=None):
    cursor = db.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()


def execute_insert(db, query, params):
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()


def fetch_and_map(db, query, model_class, params=None):
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [model_class(**dict(zip(columns, row))) for row in cursor.fetchall()]
    finally:
        cursor.close()
