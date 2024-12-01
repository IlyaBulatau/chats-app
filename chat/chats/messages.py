from core.domains import Message
from infrastructure.repositories.messages import MessageRepository


class MessageReader:
    """Читатель сообщений."""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def get_messages_from_db(self, chat_id: int) -> list[Message | None]:
        """Получить сообщения из базы данных.

        :param int chat_id: ID чата.

        :return list[`Message` | None]: Список сообщений.
        """
        return await self.message_repository.get_many_by_chat_id(chat_id)
