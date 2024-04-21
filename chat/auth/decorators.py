from functools import wraps
from typing import Coroutine

from fastapi.responses import RedirectResponse

from auth.user import is_authenticated


def login_required(controller: Coroutine):
    """Нужно что бы контроллер принимал обьект запроса"""

    @wraps(controller)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")

        if not await is_authenticated(request):
            return RedirectResponse(request.url_for("authorization_page"))

        return await controller(*args, **kwargs)

    return wrapper


def not_login(controller: Coroutine):
    """Только для не авторизаванных"""

    @wraps(controller)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")

        if await is_authenticated(request):
            return RedirectResponse(request.url_for("index"))

        return await controller(*args, **kwargs)

    return wrapper
