"""
Функции только для метода Depends из FastAPI.
"""

from typing import AsyncGenerator, Callable, TypeVar

from fastapi.requests import Request

from core.domains import User
from infrastructure.databases import database


T = TypeVar("T", bound=Callable)


async def get_current_user(request: Request) -> User | None:
    """Depends для получение текущего пользователя.

    :return User | None: Обьект пользователя если он авторизован.
    """
    user: User | None = request.state._state["user"]  # noqa: SLF001
    return user


def get_repository(repository_class: T):
    """Depends для получения иницализированного репозитория по типу репозитория.

    :param repository_class: Класс репозитория

    :return: Асинхронный генератор, который возвращает экземпляр репозитория.
    """

    async def wrapper() -> AsyncGenerator[T, None]:
        async with database.get_connection() as conn:
            yield repository_class(conn)

    return wrapper
