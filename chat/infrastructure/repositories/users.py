from decimal import ROUND_DOWN, Decimal

from asyncpg import Connection

from core.domains import User


class UserRepository:
    def __init__(self, session: Connection) -> None:
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
        query = f"SELECT id, username, email, password, files_mb FROM users WHERE {field_name} = $1"

        result = await self.session.fetchrow(query, value)

        if result:
            return User(
                id=result[0],
                username=result[1],
                email=result[2],
                password=result[3],
                files_mb=Decimal(result[4]).quantize(Decimal("0.0001"), rounding=ROUND_DOWN),
            )

        return None

    async def get_all(self) -> list[User]:
        """Получить всех пользователей.

        :return list[User]: Список пользователей.
        """
        query = "SELECT id, username, email, password FROM users"

        result = await self.session.fetch(query)

        return [User(id=row[0], username=row[1], email=row[2], password=row[3]) for row in result]

    async def increment_files_mb(self, user_id: int, files_mb: Decimal) -> None:
        """Увеличить квоту файлов пользователя.

        :param int user_id: ID пользователя.

        :param Decimal files_mb: Количество файлов.
        """
        query = "UPDATE users SET files_mb = files_mb + $1 WHERE id = $2"
        await self.session.execute(query, files_mb, user_id)
