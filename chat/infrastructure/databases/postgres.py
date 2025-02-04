from contextlib import asynccontextmanager
from typing import AsyncGenerator, NoReturn

from asyncpg import Connection, Pool, create_pool

from infrastructure.databases.base import BaseDatabase
from shared.meta_ import Singleton


class PostgresDB(BaseDatabase, metaclass=Singleton):
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: Pool = create_pool(dsn=self._dsn)

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None] | NoReturn:
        """Получение соединения к базе данных из пулла.

        :return `asyncpg.Connection`: Соедение с базой.
        """
        if not self._init:
            raise Exception("База данных не проиницилизирована")

        async with self._pool.acquire() as conn:
            yield conn

    async def get_connection_for_di(self) -> AsyncGenerator[Connection, None] | NoReturn:
        """Получение соединения к базе данных из пулла.

        :return `asyncpg.Connection`: Соедение с базой.
        """
        if not self._init:
            raise Exception("База данных не проиницилизирована")

        async with self._pool.acquire() as conn:
            yield conn

    async def close_connection(self) -> None:
        """Закрытие всех соединений пулла."""
        if not self._init:
            raise Exception("База данных не проиницилизирована")

        await self._pool.close()
        self._init = False

    async def init(self) -> None:
        """Инициализация пулла."""
        await self._pool
        self._init = True

    def is_init(self) -> bool:
        return self._init
