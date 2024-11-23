from functools import wraps
from typing import Callable

from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from auth.user import is_authenticated


def login_required(controller: Callable):
    """
    Декоратор для ендпоинтов доступных только для авторизованного пользователя.
    Нужно что бы контроллер принимал обьект запроса.
    """

    @wraps(controller)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")  # type: ignore

        if not await is_authenticated(request):
            return RedirectResponse(request.url_for("authorization_page"))

        return await controller(*args, **kwargs)

    return wrapper


def not_login(controller: Callable):
    """
    Декоратор только для не авторизованного пользователя.
    Нужно что бы контроллер принимал обьект запроса.
    """

    @wraps(controller)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")  # type: ignore

        if await is_authenticated(request):
            return RedirectResponse(request.url_for("index"))

        return await controller(*args, **kwargs)

    return wrapper
