import base64
import logging
from uuid import UUID, uuid4

from application.backgroud_tasks.tasks import remove_message_with_file, save_new_chat_message_in_db
from application.chats import exceptions
from application.chats.checkers import is_message_sender
from application.chats.schemas import FileData
from application.chats.services.files import FileMessageCreator
from application.chats.validators import SendFile, SendMessage
from application.dto.files import FileReadDTO
from application.dto.messages import MessageReadDTO
from application.files.files import (
    calculate_file_size_from_bytes_to_mb,
    get_file_type,
    get_filename,
)
from application.users.files_quota import is_available_user_quota_for_file
from core.domains import User
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.messages import MessageRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage


logger = logging.getLogger("uvicorn")


class MessageReader:
    """Читатель сообщений."""

    def __init__(self, message_repository: MessageRepository, flie_storage: FileStorage):
        self.message_repository = message_repository
        self.file_storage = flie_storage

    async def get_messages_from_db(self, chat_id: int) -> list[MessageReadDTO] | None:
        """Получить сообщения из базы данных.

        :param int chat_id: ID чата.

        :return list[`MessageReadDTO`] | None: Список сообщений.
        """
        messages = await self.message_repository.get_many_by_chat_id(chat_id)

        if not messages:
            return None

        result = []

        for message in messages:
            if message.file:
                name = get_filename(message.file)
                url = await self.file_storage.get_object_url(message.file)
                type = get_file_type(message.file)  # noqa: A001
                file = FileReadDTO(name=name, url=url, type=type)
            else:
                file = None

            result.append(
                MessageReadDTO(
                    id=message.id,
                    uid=message.uid,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    text=message.text,
                    created_at=message.created_at,
                    file=file,
                )
            )

        return result


class MessageCreator:
    """Создатель сообщений."""

    def __init__(
        self,
        user_repository: UserRepository,
        message_repository: MessageRepository,
        chat_repository: ChatRepository,
        file_storage: FileStorage,
        file_message_creator: FileMessageCreator,
    ):
        """
        :param `UserRepository` user_repository: Репозиторий пользователей.

        :param `MessageRepository` message_repository: Репозиторий сообщений.

        :param `ChatRepository` chat_repository: Репозиторий чатов.

        :param `FileStorage` file_storage: Хранилище файлов.

        :param `FileMessageCreator` file_message_creator: Создатель файлов.
        """
        self.user_repository = user_repository
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.file_storage = file_storage
        self.file_message_creator = file_message_creator

    async def create(
        self,
        chat_uid: UUID,
        sender_id: int,
        text: str,
        file: FileData | None,
    ) -> SendMessage:
        """
        Сохранение файла из сообщения в хранилище
        и запуск задачи для сохранения в базе данных.

        :param UUID chat_uid: UID чата.

        :param int sender_id: ID отправителя.

        :param str text: Текст сообщения.

        :param `FileData` | None file: Файл.

        :return `SendMessage`
        """
        chat = await self.chat_repository.get_by_uid_and_member(chat_uid, sender_id)

        if not chat:
            logger.info(f"Recieve message: chat with UID: {chat_uid} not found")
            raise exceptions.ChatNotFoundError("Chat not found")

        if file:
            file_content: str = file.get("content")  # type: ignore
            filename: str = file.get("filename")  # type: ignore

            file_size = calculate_file_size_from_bytes_to_mb(len(base64.b64decode(file_content)))

            # getting fresh user data
            user = await self.user_repository.get_by("id", sender_id)

            # maybe
            if not user:
                logger.info(f"Recieve message: user with UID: {sender_id} not found")
                raise exceptions.UserNotFoundError()

            if not is_available_user_quota_for_file(user.files_mb, file_size):
                logger.info("User quota limit exceeded")
                raise exceptions.FileQuotaSizeError()

            file_url = await self.file_message_creator.create(chat.uid, filename, file_content)

            await self.user_repository.increment_files_mb(sender_id, file_size)

            representation_file_url = await self.file_storage.get_object_url(file_url)

            send_file = SendFile(
                name=filename,
                url=representation_file_url,
                type=get_file_type(filename),
            )
        else:
            send_file = None
            file_url = None

        message_uid = uuid4()

        await save_new_chat_message_in_db.kiq(
            chat.id,
            message_uid,
            sender_id,
            text,
            file=file_url,
        )

        return SendMessage(
            chat_uid=chat_uid, uid=message_uid, sender_id=sender_id, text=text, file=send_file
        )


class MessageRemover:
    """Удаление сообщений."""

    def __init__(self, message_repository: MessageRepository):
        """
        :param `MessageRepository` message_repository: Репозиторий сообщений.
        """
        self.message_repository = message_repository

    async def remove(self, message_uid: UUID, sender: User) -> None:
        """
        Перед удалением проверяет сообщение на принадлежность отправителю.
        Если сообщение содержит файл, запускает задачу по удалению файла.

        :param UUID message_uid: UID сообщения

        :return None
        """

        message = await self.message_repository.get_by("uid", message_uid)

        if not message:
            logger.info(f"Recieve message: message with UID: {message_uid} not found")
            raise exceptions.MessageNotFoundError("Message not found")

        if not is_message_sender(sender, message):
            logger.info("Permission denied to delete message by user")
            raise exceptions.PermissionDeniedDeleteMessageError(
                "Permission denied to delete message"
            )

        if message.file:
            await remove_message_with_file.kiq(message.file, sender.id)

        await self.message_repository.delete_by("uid", message_uid)
