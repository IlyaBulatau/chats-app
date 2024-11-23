from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from auth.decorators import login_required
from core.dependencies import get_current_user
from core.domains import User
from settings import BASE_DIR


router = APIRouter(tags=["chats"], prefix="/chats")
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/", response_class=HTMLResponse)
@login_required
async def index(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})


@router.get("/{chat_id}", response_class=HTMLResponse)
@login_required
async def get_chat_by_id(
    request: Request,
):
    return templates.TemplateResponse(request=request, name="chat.html")
