from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import auth_routes, menu_routes, order_routes, customer_routes, employee_routes, category_routes, image_routes, report_routes, templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_routes.router, tags=["auth"])
app.include_router(menu_routes.router, tags=["menu operations"])
app.include_router(category_routes.router, tags=["category operations"])
app.include_router(order_routes.router, tags=["orders operations"])
app.include_router(customer_routes.router, tags=["customers operation"])
app.include_router(employee_routes.router, tags=["employee operations"])
app.include_router(image_routes.router, tags=["images operations"])
app.include_router(report_routes.router, tags=["reports"])
app.include_router(templates.router, tags=["templates"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)