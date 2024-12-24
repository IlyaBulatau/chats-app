import logging
import uuid

from core.domains import Chat, User
from core.use_cases.checkers import is_chat_member
from dto.chats import ChatInfoDTO
from infrastructure.repositories.chats import ChatRepository


logger = logging.getLogger("uvicorn")


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

        logging.info("Chat created. ID: %s", chat_id)

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


class ChatReader:
    """Класс для получения информации о чате."""

    def __init__(self, chat_repository: ChatRepository, member: User) -> None:
        self.chat_repository = chat_repository
        self.member = member

    async def get_chat_info_by_id(self, chat_id: int) -> ChatInfoDTO | None:
        """
        Получить чат по ID. Если чат не существует или
        текущего пользователя нету в чате, вернуть None.

        :param int chat_id: ID чата.

        :return `ChatInfoDTO` | None: Чат или None.
        """
        chat_info = await self.chat_repository.get_by_id(chat_id)

        if not chat_info:
            return None

        if not is_chat_member(self.member, chat_info.chat):
            return None

        return chat_info
