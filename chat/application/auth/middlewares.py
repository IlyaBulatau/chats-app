from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from application.auth.user import current_user
from settings import SESSION_SETTINGS


class AddCurrentUserToRequestMiddleware(BaseHTTPMiddleware):
    """
    Добавляет обьект авторизованного пользователя к обьекту запроса.
    Нужно для получения текущего пользователя в html шаблонах.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        user = await current_user(request.cookies.get(SESSION_SETTINGS.auth_key))
        request.state._state["user"] = user if user else None  # noqa: SLF001
        return await call_next(request)
