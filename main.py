from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import auth_routes, menu_routes, order_routes, customer_routes, employee_routes, category_routes, image_routes, report_routes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_routes.router)
app.include_router(menu_routes.router)
app.include_router(order_routes.router)
app.include_router(customer_routes.router)
app.include_router(employee_routes.router)
app.include_router(category_routes.router)
app.include_router(image_routes.router)
app.include_router(report_routes.router)

templates = Jinja2Templates(directory="static")


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/test/", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")
