from typing import AsyncGenerator, TypeVar

from fastapi.requests import Request
from infrastructure.databases import database

from core.domains import User


T = TypeVar("T")


async def get_current_user(request: Request) -> User | None:
    user: User | None = request.state._state["user"]  # noqa: SLF001
    return user


def get_repository(repository_class: T):
    async def wrapper() -> AsyncGenerator[T, None]:
        async with database.get_connection() as conn:
            yield repository_class(conn)

    return wrapper
