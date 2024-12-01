"""
Функции только для метода Depends из FastAPI.
"""

from typing import AsyncGenerator, Callable, TypeVar

from infrastructure.databases import database


T = TypeVar("T", bound=Callable)


def get_repository(repository_class: T):
    """Depends для получения иницализированного репозитория по типу репозитория.

    :param repository_class: Класс репозитория

    :return: Асинхронный генератор, который возвращает экземпляр репозитория.
    """

    async def wrapper() -> AsyncGenerator[T, None]:
        async with database.get_connection() as conn:
            yield repository_class(conn)

    return wrapper
