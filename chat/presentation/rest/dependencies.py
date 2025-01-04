from typing import NoReturn

from fastapi import Cookie

from application.auth.user import current_user
from core.domains import User
from presentation.rest.exceptions import APIUnauthorizedError


async def get_current_user_api(sessionid: str | None = Cookie(default=None)) -> User | NoReturn:
    """Depends для получение текущего пользователя.

    :param str | None sessionid: ID сессии в куках.

    :return User | NoReturn: Обьект пользователя если он авторизован.
    """
    user: User | None = await current_user(sessionid)

    if not user:
        raise APIUnauthorizedError()

    return user
