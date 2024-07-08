from fastapi import APIRouter, Depends, HTTPException
from models import AuthDetails, Employee
from auth import AuthHandler
from helpers import fetch_and_map, get_db_connection, execute_query

router = APIRouter()
auth_handler = AuthHandler()

@router.post('/api/login/')
def login(auth_details: AuthDetails, db=Depends(get_db_connection)):
    query = """
    SELECT e.employee_id, e.first_name, e.employee_code, c.password
    FROM Employees e
    JOIN Credentials c ON e.employee_id = c.employee_id
    WHERE e.employee_code = %s
    """
    result = execute_query(db, query, (auth_details.employee_code,))

    if not result:
        raise HTTPException(status_code=401, detail="Invalid employee code")
    employee = result[0]
    employee_code = employee[2]
    hashed_password = employee[3]
    if not auth_handler.verify_password(auth_details.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    token = auth_handler.encode_token(employee_code)
    return {'token': token}


@router.get("/api/me/", response_model=Employee)
def me(db=Depends(get_db_connection), code=Depends(auth_handler.auth_wrapper)):
    query = "SELECT * FROM `Employees` WHERE employee_code = %s;"
    result = fetch_and_map(db, query, Employee, (code,))
    if not result:
        raise HTTPException(500, detail="User is not found")
    return result[0]
