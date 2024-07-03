from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="static")


@router.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/dashboard/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@router.get("/test/", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")
