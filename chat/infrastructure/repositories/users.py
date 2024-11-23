from asyncpg import Connection

from dto.users import UserDTO


class UserRepository:
    def __init__(self, session: Connection):
        self.session: Connection = session

    async def add(self, username: str, email: str, password: str | None = None) -> int:
        query = "INSERT INTO users (username, email, password) VALUES($1, $2, $3) RETURNING id"

        result: int = await self.session.fetchval(query, username, email, password)

        return result

    async def get_by_id(self, id_: int) -> UserDTO | None:
        query = "SELECT id, username, email, password FROM users WHERE id = $1"

        result = await self.session.fetchrow(query, id_)

        if result:
            return UserDTO(id=result[0], username=result[1], email=result[2], password=result[3])

        return None

    async def get_by_email(self, email: str) -> UserDTO | None:
        query = "SELECT id, username, email, password FROM users WHERE email = $1"

        result = await self.session.fetchrow(query, email)

        if result:
            return UserDTO(id=result[0], username=result[1], email=result[2], password=result[3])

        return None
