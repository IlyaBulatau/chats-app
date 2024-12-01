from functools import wraps
from typing import Any, Callable

from infrastructure.databases import database


def init_database(function: Callable) -> Callable:
    """Декоратор для инициализации базы данных в бекграунд задачах."""

    @wraps(function)
    async def wrapper(*args, **kwargs) -> Any:
        if not database.is_init():
            await database.init()

        return await function(*args, **kwargs)

    return wrapper
