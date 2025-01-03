from typing import NoReturn

from fastapi import Cookie, status
from fastapi.exceptions import HTTPException

from application.auth.user import current_user
from core.domains import User


async def get_current_user(sessionid: str | None = Cookie(default=None)) -> User | NoReturn:
    """Depends для получение текущего пользователя.

    :param str | None sessionid: ID сессии в куках.

    :return User | NoReturn: Обьект пользователя если он авторизован.
    """
    user: User | None = await current_user(sessionid)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNATHORIZED")

    return user
