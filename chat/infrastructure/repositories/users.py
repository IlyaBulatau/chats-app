from asyncpg import Connection

from core.domains import User


class UserRepository:
    def __init__(self, session: Connection):
        self.session: Connection = session

    async def add(self, username: str, email: str, password: str | None = None) -> int:
        """Добавить пользователя в базу.

        :param str username: Имя пользователя.

        :param str email: Адрес электронной почты.

        :param str | None password: Пароль пользователя.

        :return int: ID пользователя.
        """
        query = "INSERT INTO users (username, email, password) VALUES($1, $2, $3) RETURNING id"

        result: int = await self.session.fetchval(query, username, email, password)

        return result

    async def get_by(self, field_name: str, value: str | int) -> User | None:
        """Получить пользователя по полю.

        :param str field_name: Имя поля.

        :param int | str value: Значение поля.

        :return User | None: Пользователь или None.
        """
        query = f"SELECT id, username, email, password FROM users WHERE {field_name} = $1"

        result = await self.session.fetchrow(query, value)

        if result:
            return User(id=result[0], username=result[1], email=result[2], password=result[3])

        return None
