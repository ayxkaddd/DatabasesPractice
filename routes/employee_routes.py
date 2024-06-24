import random
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import Employee
from mysql.connector import Error

from helpers import get_db_connection, fetch_and_map, execute_insert, execute_query
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.get("/api/employees/", response_model=List[Employee])
def get_employees(db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    query = "SELECT * FROM Employees;"
    return fetch_and_map(db, query, Employee)


@router.post('/api/employees/', status_code=201)
def create_employee(employee: Employee, db=Depends(get_db_connection), _=Depends(auth_handler.auth_wrapper)):
    if not employee.password:
        raise HTTPException(status_code=400, detail="Password is required")

    while True:
        employee_code = random.randint(1000, 9999)
        query = "SELECT COUNT(*) FROM Employees WHERE employee_code = %s"
        result = execute_query(db, query, (employee_code,))
        if result[0][0] == 0:
            break

    hashed_password = auth_handler.get_password_hash(employee.password)

    try:
        employee_query = """
        INSERT INTO Employees (first_name, last_name, employee_code)
        VALUES (%s, %s, %s)
        """
        employee_id = execute_insert(db, employee_query, (employee.first_name, employee.last_name, employee_code))

        credentials_query = """
        INSERT INTO Credentials (employee_id, password)
        VALUES (%s, %s)
        """
        execute_insert(db, credentials_query, (employee_id, hashed_password))
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
