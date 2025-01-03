from uuid import UUID

from asyncpg import Connection

from application.dto.chats import ChatInfoDTO
from core.domains import Chat, User


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
            SELECT 
                id, uid, creator_id, companion_id, created_at, updated_at 
            FROM 
                chats 
            WHERE 
                creator_id = $1 AND companion_id = $2 OR creator_id = $2 AND companion_id = $1
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

    async def get_by_id(self, chat_id: int) -> ChatInfoDTO | None:
        """Получить информацию о чате по ID.

        :param int chat_id: ID чата.

        :return `ChatInfoDTO` | None: Информация о чате или None.
        """
        query = """
        SELECT 
            c.id AS chat_id,
            c.uid AS uid,
            c.creator_id AS chat_creator_id,
            c.companion_id AS chat_companion_id,
            c.created_at AS created_at,
            c.updated_at AS updated_at,
            creator.id AS creator_id, 
            creator.username AS creator_username,
            creator.email AS creator_email,
            companion.id AS companion_id, 
            companion.username AS companion_username,
            companion.email AS companion_email
        FROM chats AS c
            JOIN users AS creator ON creator.id = c.creator_id
            JOIN users AS companion ON companion.id = c.companion_id
        WHERE c.id = $1"""

        result = await self.session.fetchrow(query, chat_id)

        if result:
            return ChatInfoDTO(
                chat=Chat(
                    id=result.get("chat_id"),
                    uid=result.get("uid"),
                    creator_id=result.get("chat_creator_id"),
                    companion_id=result.get("chat_companion_id"),
                    created_at=result.get("created_at"),
                    updated_at=result.get("updated_at"),
                ),
                creator=User(
                    id=result.get("creator_id"),
                    username=result.get("creator_username"),
                    email=result.get("creator_email"),
                ),
                companion=User(
                    id=result.get("companion_id"),
                    username=result.get("companion_username"),
                    email=result.get("companion_email"),
                ),
            )

        return None

    async def get_by_uid_and_member(self, uid: UUID, member_id: int) -> Chat | None:
        """Получить чат по уникальному идентификатору и ID участника.

        :param UUID uid: Уникальный идентификатор чата.

        :param int member_id: ID участника чата.

        :return `Chat` | None: Чат или None.
        """
        query = """
            SELECT 
                id, uid, creator_id, companion_id, created_at, updated_at 
            FROM 
                chats 
            WHERE 
                uid = $1 AND (creator_id = $2 OR companion_id = $2)
        """

        result = await self.session.fetchrow(query, uid, member_id)

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
