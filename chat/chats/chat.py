import uuid

from core.domains import Chat
from infrastructure.repositories.chats import ChatRepository


class ChatCreator:
    """Класс для создания чата."""

    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def create(self, creator_id: int, companion_id: int) -> int:
        """Создает чат если он не существует. Возвращает ID чата.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return int: ID чата.
        """
        existing_chat = await self.get_existing_chat(creator_id, companion_id)

        if existing_chat:
            return existing_chat.id

        chat_id: int = await self.chat_repository.add(
            uid=uuid.uuid4(), creator_id=creator_id, companion_id=companion_id
        )

        return chat_id

    async def get_existing_chat(self, creator_id: int, companion_id: int) -> Chat | None:
        """Получить существующий чат по уникальному сочитанию создателя и собеседника.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return `Chat` | None: Чат или None.
        """
        return await self.chat_repository.get_by_creator_companion_together(
            creator_id, companion_id
        )
