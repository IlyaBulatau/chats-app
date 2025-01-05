import logging
import uuid

from application.chats.checkers import is_chat_member
from application.dto.chats import ChatInfoDTO, ChatReadDTO
from core.domains import User
from core.exceptions import ChatNotFound, CompanionNotExists, IsNotChatMember
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.users import UserRepository


logger = logging.getLogger("uvicorn")


class ChatCreator:
    """Класс для создания чата."""

    def __init__(self, chat_repository: ChatRepository, user_repository: UserRepository) -> None:
        self.chat_repository = chat_repository
        self.user_repository = user_repository

    async def create(self, creator_id: int, companion_id: int) -> int:
        """Создает чат если он не существует. Возвращает ID чата.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return int: ID чата.
        """
        existing_chat = await self.get_existing_chat(creator_id, companion_id)

        if existing_chat:
            return existing_chat.id

        existing_companion_chat = await self.user_repository.get_by("id", companion_id)

        if not existing_companion_chat:
            raise CompanionNotExists(field="companion_id")

        chat_id: int = await self.chat_repository.add(
            uid=uuid.uuid4(), creator_id=creator_id, companion_id=companion_id
        )

        logging.info("Chat created. ID: %s", chat_id)

        return chat_id

    async def get_existing_chat(self, creator_id: int, companion_id: int) -> ChatReadDTO | None:
        """Получить существующий чат по уникальному сочитанию создателя и собеседника.

        :param int creator_id: ID создателя чата.

        :param int companion_id: ID собеседника чата.

        :return `Chat` | None: Чат или None.
        """
        chat = await self.chat_repository.get_by_creator_companion_together(
            creator_id, companion_id
        )

        if not chat:
            return None

        return ChatReadDTO(
            id=chat.id,
            uid=chat.uid,
            creator_id=chat.creator_id,
            companion_id=chat.companion_id,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )


class ChatReader:
    """Класс для получения информации о чате."""

    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def get_chat_info_by_id(self, chat_id: int, chat_member: User) -> ChatInfoDTO:
        """
        Получить чат по ID. Если чат не существует или
        текущего пользователя нету в чате, вернуть None.

        :param int chat_id: ID чата.

        :return `ChatInfoDTO` | None: Чат или None.
        """
        chat_info = await self.chat_repository.get_by_id(chat_id)

        if not chat_info:
            raise ChatNotFound(field="chat_id")

        if not is_chat_member(chat_member, chat_info.chat):
            raise IsNotChatMember()

        return chat_info
