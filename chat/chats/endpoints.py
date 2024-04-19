from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from settings import BASE_DIR

router = APIRouter(tags=["chats"], prefix="/chats")
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")