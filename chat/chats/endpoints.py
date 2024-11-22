from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from auth.decorators import login_required
from chats.use_cases.chats import get_chats_by_id, get_chats_list
from core.dependencies import get_current_user
from core.domains import Chat, User
from settings import BASE_DIR


router = APIRouter(tags=["chats"], prefix="/chats")
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/", response_class=HTMLResponse)
@login_required
async def index(
    request: Request,
    user: User = Depends(get_current_user),
    chats: list[Chat] = Depends(get_chats_list),
):
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user, "chats": chats})


@router.get("/{chat_id}", response_class=HTMLResponse)
@login_required
async def get_chat_by_id(
    request: Request,
    chat: Chat = Depends(get_chats_by_id),
):
    return templates.TemplateResponse(request=request, name="chat.html", context={"chat": chat})
