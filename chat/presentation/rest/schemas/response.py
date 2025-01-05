"""Схемы ответов.
Все схемы которые начинаяются с нижнего подчеркивания являются внутренними и
используются для генерации полной схемы которая включает в себя `SuccessResponseSchema`.
Схемы которые наследуются от `SuccessResponseSchema` прикрепляются к ендпоинтам.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SuccessResponseSchema(BaseModel):
    """Схема успешного ответа. От этой схемы наследуются другие ответы."""

    success: bool = True
    result: dict[str, Any] | list[dict[str, Any] | None] | None = None


class ExceptionResponseSchema(BaseModel):
    """Схема исключения."""

    success: bool = False
    error: str
    result: dict[str, str]


class _ReceiveMeResponseSchema(BaseModel):
    """Схема получения информации о себе."""

    id: int
    username: str
    email: str
    files_mb: float


class ReceiveMeResponseSchema(SuccessResponseSchema):
    """Схема получения информации о себе."""

    result: _ReceiveMeResponseSchema  # type: ignore


class _CreateChatResponseSchema(BaseModel):
    """Схема ответа создания чата."""

    chat_id: int


class CreateChatResponseSchema(SuccessResponseSchema):
    """Схема ответа создания чата."""

    result: _CreateChatResponseSchema  # type: ignore


class _ReceiveChatInfoResponseSchema(BaseModel):
    """Схема получения информации о чате."""

    chat_id: int
    creator_id: int
    companion_id: int


class ReceiveChatInfoResponseSchema(SuccessResponseSchema):
    """Схема получения информации о чате."""

    result: _ReceiveChatInfoResponseSchema  # type: ignore


class _ReceiveMessageResponseSchema(BaseModel):
    """Схема получения информации о сообщении."""

    id: int
    uid: UUID
    chat_id: int
    sender_id: int
    text: str
    created_at: str
    file: str


class ReceiveMessagesResponseSchema(SuccessResponseSchema):
    """Схема получения информации о сообщении."""

    result: list[_ReceiveMessageResponseSchema]  # type: ignore


class _ReceiveUserResponseSchema(BaseModel):
    """Схема получения информации о пользователе."""

    id: int
    username: str


class ReceiveUsersResponseSchema(SuccessResponseSchema):
    """Схема получения информации о пользователях."""

    result: list[_ReceiveUserResponseSchema]  # type: ignore
