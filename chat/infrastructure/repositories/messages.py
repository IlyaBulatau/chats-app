from asyncpg import Connection

from core.domains import Message


class MessageRepository:
    def __init__(self, session: Connection) -> None:
        self.session: Connection = session

    async def add(self, chat_id: int, sender_id: int, text: str | None, file: str | None) -> int:
        """Добавить сообщение в базу.

        :param int chat_id: ID чата.

        :param int sender_id: ID отправителя.

        :param str text | None: Текст сообщения.

        :param str file | None: Путь к файлу.

        :return int: ID сообщения.
        """
        query = """
            INSERT INTO messages (chat_id, sender_id, text, file) 
            VALUES($1, $2, $3, $4) RETURNING id
        """

        result: int = await self.session.fetchval(query, chat_id, sender_id, text, file)

        return result

    async def get_many_by_chat_id(self, chat_id: int) -> list[Message] | None:
        query = """
            SELECT id, uid, chat_id, sender_id, text, created_at, file 
            FROM messages 
            WHERE chat_id = $1 ORDER BY created_at
        """

        messages = await self.session.fetch(query, chat_id)

        return [
            Message(
                id=message[0],
                uid=message[1],
                chat_id=message[2],
                sender_id=message[3],
                text=message[4],
                created_at=message[5],
                file=message[6],
            )
            for message in messages
        ]
