from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, status

from application.chats.services.chats import ChatCreator, ChatReader
from application.chats.services.messages import MessageReader
from containers import Container
from core.domains import User
from core.exceptions import ChatNotFound, CustomException, IsNotChatMember
from presentation.rest.dependencies import get_current_user_api
from presentation.rest.representations import exception_representation, success_representation
from presentation.rest.schemas.request import CreateChatRequestSchema
from presentation.rest.schemas.response import (
    CreateChatResponseSchema,
    ExceptionResponseSchema,
    ReceiveChatInfoResponseSchema,
    ReceiveMessagesResponseSchema,
)


router = APIRouter(prefix="/api/v1/chats", tags=["Чаты"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание чата, если чат уже создан, то возвращает ID чата.",
    response_description="При успешном создании возвращает код 201 и ID чата.",
    responses={
        201: {"model": CreateChatResponseSchema},
        400: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
        401: {
            "model": None,
        },
    },
)
@inject
async def create_chat(
    create_data: CreateChatRequestSchema,
    current_user: User = Depends(get_current_user_api),
    chat_creator: ChatCreator = Depends(Provide[Container.chat_creator]),
):
    """Создание чата, если чат уже создан, то возвращает ID чата."""

    try:
        chat_id: int = await chat_creator.create(current_user.id, create_data.companion_id)
    except CustomException as exc:
        return exception_representation(exc)

    return success_representation({"chat_id": chat_id}, stauts_code=status.HTTP_201_CREATED)


@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    summary="Получение информации о чате",
    response_description="Возвращает информацию о чате.",
    responses={
        200: {"model": ReceiveChatInfoResponseSchema},
        400: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
        401: {"model": None},
        403: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
    },
)
@inject
async def get_chat_info_by_id(
    chat_id: int = Path(description="ID чата"),
    current_user: User = Depends(get_current_user_api),
    chat_reader: ChatReader = Depends(Provide[Container.chat_reader]),
):
    try:
        chat_info = await chat_reader.get_chat_info_by_id(chat_id, current_user)
    except ChatNotFound as exc:
        return exception_representation(exc, status_code=status.HTTP_404_NOT_FOUND)
    except IsNotChatMember as exc:
        return exception_representation(exc, status_code=status.HTTP_403_FORBIDDEN)

    return success_representation(
        {
            "chat_id": chat_info.chat.id,
            "creator_id": chat_info.creator.id,
            "companion": chat_info.companion.id,
        }
    )


@router.get(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="Получение сообщений чата.",
    response_description="Возвращает список сообщений чата.",
    responses={
        200: {"model": ReceiveMessagesResponseSchema},
        400: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
        401: {"model": None},
        403: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
    },
)
@inject
async def get_messages_by_chat_id(
    chat_id: int,
    current_user: User = Depends(get_current_user_api),
    message_reader: MessageReader = Depends(Provide[Container.message_reader]),
):
    """Получение сообщений чата."""

    try:
        messages = await message_reader.get_messages_from_db(chat_id, current_user)
    except ChatNotFound as exc:
        return exception_representation(exc, status_code=status.HTTP_404_NOT_FOUND)
    except IsNotChatMember as exc:
        return exception_representation(exc, status_code=status.HTTP_403_FORBIDDEN)

    if not messages:
        return success_representation([])

    return success_representation(
        [
            {
                "id": message.id,
                "uid": message.uid,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "created_at": message.created_at,
                "text": message.text,
                "file": message.file,
            }
            for message in messages
        ]
    )
