from uuid import UUID

from asyncpg import Connection

from core.domains import Chat


class ChatRepository:
    def __init__(self, session: Connection) -> None:
        self.session: Connection = session

    async def add(self, uid: UUID, creator_id: int, companion_id: int) -> int:
        """Добавить чат в базу.

        :param UUID uid: Уникальный идентификатор чата.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return int: ID чата.
        """
        query = "INSERT INTO chats (uid, creator_id, companion_id) VALUES($1, $2, $3) RETURNING id"

        result: int = await self.session.fetchval(query, uid, creator_id, companion_id)

        return result

    async def get_by_creator_companion_together(
        self, creator_id: int, companion_id: int
    ) -> Chat | None:
        """Получить чат по уникальному сочитанию создателя и собеседника.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return `Chat` | None: Чат или None.
        """
        query = """
            SELECT id, uid, creator_id, companion_id, created_at, updated_at 
            FROM chats 
            WHERE creator_id = $1 AND companion_id = $2
        """

        result = await self.session.fetchrow(query, creator_id, companion_id)

        if result:
            return Chat(
                id=result[0],
                uid=result[1],
                creator_id=result[2],
                companion_id=result[3],
                created_at=result[4],
                updated_at=result[5],
            )

        return None
