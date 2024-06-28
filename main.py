from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import auth_routes, menu_routes, order_routes, customer_routes, employee_routes, category_routes, image_routes, report_routes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

app.include_router(auth_routes.router, tags=["auth"])
app.include_router(menu_routes.router, tags=["menu operations"])
app.include_router(category_routes.router, tags=["category operations"])
app.include_router(order_routes.router, tags=["orders operations"])
app.include_router(customer_routes.router, tags=["customers operation"])
app.include_router(employee_routes.router, tags=["employee operations"])
app.include_router(image_routes.router, tags=["images operations"])
app.include_router(report_routes.router, tags=["reports"])


@app.get("/", response_class=HTMLResponse, tags=["templates"])
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login/", response_class=HTMLResponse, tags=["templates"])
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard/", response_class=HTMLResponse, tags=["templates"])
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/test/", response_class=HTMLResponse, tags=["templates", "testing"])
def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")
