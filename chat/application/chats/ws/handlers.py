from abc import ABC, abstractmethod
import logging

from application.backgroud_tasks.tasks import save_new_chat_message_in_db
from application.chats.services.files import FileMessageCreator
from application.chats.ws import exceptions
from application.chats.ws.schemas import NewMessageData
from application.chats.ws.validators import ReceivedMessage, SendFile, SendMessage
from application.files.files import calculate_file_size_from_bytes_representation, get_file_type
from application.users.files_quota import is_available_user_quota_for_file
from core.domains import User
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage


logger = logging.getLogger("uvicorn")


class BaseMessageHandler(ABC):
    @abstractmethod
    async def handle(self, message: NewMessageData): ...


class NewMessageHandler(BaseMessageHandler):
    """Создает новое сообщение в чате."""

    def __init__(
        self,
        chat_repository: ChatRepository,
        user_repository: UserRepository,
        file_storage: FileStorage,
        sender: User,
    ):
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.file_storage = file_storage
        self.sender = sender

    async def handle(self, message: NewMessageData) -> SendMessage:
        """
        Валиация сообщения, сохранение файла из сообщения в хранилище
        и запуск задачи для сохранения в базе данных.

        :param `NewMessageData` message: Данные сообщения.

        :return: `SendMessage`
        """
        try:
            data = ReceivedMessage(sender_id=self.sender.id, **message)
        except ValueError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            raise exceptions.InvalidJsonDataError("Invalid json message")

        chat = await self.chat_repository.get_by_uid_and_member(data.chat_uid, data.sender_id)

        if not chat:
            logger.info(f"Recieve message: chat with UID: {data.chat_uid} not found")
            raise exceptions.ChatNotFoundError("Chat not found")

        if data.file:
            file_size = calculate_file_size_from_bytes_representation(
                data.file.content.encode("utf-8")
            )

            # getting fresh user data
            user = await self.user_repository.get_by("id", self.sender.id)

            # maybe
            if not user:
                logger.info(f"Recieve message: user with UID: {data.sender_id} not found")
                raise exceptions.UserNotFoundError()

            if not is_available_user_quota_for_file(user.files_mb, file_size):
                logger.info("User quota limit exceeded")
                raise exceptions.FileQuotaSizeError()

            file_url = await FileMessageCreator(self.file_storage, data.file).create(chat.uid)

            await self.user_repository.increment_files_mb(self.sender.id, file_size)

            representation_file_url = await self.file_storage.get_object_url(file_url)

            send_file = SendFile(
                name=data.file.filename,
                url=representation_file_url,
                type=get_file_type(data.file.filename),
            )
        else:
            send_file = None
            file_url = None

        await save_new_chat_message_in_db.kiq(chat.id, data.sender_id, data.text, file=file_url)

        return SendMessage(
            chat_uid=data.chat_uid, sender_id=data.sender_id, text=data.text, file=send_file
        )


class DeleteMessageHandler(BaseMessageHandler):
    async def handle(self, message: NewMessageData): ...
