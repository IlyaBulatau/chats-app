from fastapi import APIRouter, Depends, Form, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from application.auth.dependencies import get_current_user
from application.chats.services.chats import ChatCreator, ChatReader
from application.chats.services.messages import MessageReader
from core.domains import User
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.messages import MessageRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage
from settings import BASE_DIR
from shared.dependencies import get_repository


router = APIRouter(tags=["chats"], prefix="/chats")
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    users: list[User] = await user_repository.get_all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"current_user": current_user, "users": users}
    )


@router.post("/", response_class=HTMLResponse)
async def create_chat(
    request: Request,
    current_user: User = Depends(get_current_user),
    chat_repository: ChatRepository = Depends(get_repository(ChatRepository)),
    companion_id: int = Form(description="ID пользователя с которым создать чат"),
    redirect_url_for: str = "get_chat_by_id",
):
    chat_creator = ChatCreator(chat_repository)

    chat_id: int = await chat_creator.create(current_user.id, companion_id)

    redirect_url = request.url_for(redirect_url_for, chat_id=chat_id)

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/{chat_id}", response_class=HTMLResponse)
async def get_chat_by_id(
    request: Request,
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_repository: ChatRepository = Depends(get_repository(ChatRepository)),
):
    chat_reader = ChatReader(chat_repository, current_user)

    chat_info = await chat_reader.get_chat_info_by_id(chat_id)

    if not chat_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "chat": chat_info.chat,
            "creator": chat_info.creator,
            "companion": chat_info.companion,
            "user": current_user,
        },
    )


@router.get("/{chat_id}/messages")
async def get_messages_by_chat_id(
    chat_id: int,
    current_user: User = Depends(get_current_user),  # noqa: ARG001
    message_repository: MessageRepository = Depends(get_repository(MessageRepository)),
    file_storage: FileStorage = Depends(FileStorage),
):
    message_reader = MessageReader(message_repository, file_storage)

    return await message_reader.get_messages_from_db(chat_id)
