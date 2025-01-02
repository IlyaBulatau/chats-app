import json
from json import JSONDecodeError
import logging
from uuid import UUID

from fastapi import WebSocket, WebSocketException, status

from application.backgroud_tasks.tasks import save_new_chat_message_in_db
from application.chats.services.files import FileMessageCreator
from application.chats.ws.schemas import NewMessageData
from application.chats.ws.validators import ReceivedMessage, SendFile, SendMessage
from application.files.files import calculate_file_size_from_bytes_representation, get_file_type
from application.users.files_quota import is_available_user_quota_for_file
from core.constants import USER_FILES_QUOTA_MB
from core.domains import Chat, User
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage
from settings import WS_CHAT_CONNECTIONS


logger = logging.getLogger("uvicorn")


class WebsocketChatManager:
    def __init__(
        self,
        websocket: WebSocket,
        chat_uid: UUID,
        current_user: User,
        chat_repository: ChatRepository,
        user_repository: UserRepository,
        file_storage: FileStorage,
    ):
        """Инициализация менеджера для работы с чатами.

        :param `WebSocket` websocket: Объект WebSocket.

        :param `UUID` chat_uid: Уникальный идентификатор чата.

        :param `User` current_user: Текущий пользователь.

        :param `ChatRepository` chat_repository: Репозиторий чатов.

        :param `UserRepository` user_repository: Репозиторий пользователей.

        :param `FileStorage` file_storage: Хранилище файлов.
        """
        self.websocket = websocket
        self.chat_uid = chat_uid
        self.current_user = current_user
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.file_storage = file_storage
        self.message_send: SendMessage | None = None

        self._add_connection(self.chat_uid)

    async def receive_message(self) -> None:
        """Получить и обработать сообщение от клиента."""
        try:
            data: NewMessageData = await self.websocket.receive_json()
            await self.save_message(data, self.current_user)
        except JSONDecodeError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            await self.websocket.send_text("Invalid JSON")
            raise WebSocketException(status.WS_1003_UNSUPPORTED_DATA, "Invalid JSON")

    async def broadcast_message(self) -> None:
        """Отправить сообщение всем подключенным к чату клиентам."""
        if self.message_send:
            for connection in WS_CHAT_CONNECTIONS[self.chat_uid]:
                await connection.send_text(self.message_send.model_dump_json())

    async def answer_error_message(self, message: str | None) -> None:
        """Отправить сообщение об ошибке клиенту отправившиму сообщение."""
        await self.websocket.send_text(json.dumps({"error": message}))

    async def save_message(self, message: NewMessageData, sender: User):
        """
        Валидация сообщения, сохранение файла в s3, если он есть в сообщении,
        запуск задачи для сохранения сообщения в базе данных.

        :param `NewMessageData` message: Данные сообщения.

        :param `User` sender: Пользователь отправивший сообщение.

        :return None:
        """
        try:
            data = ReceivedMessage(sender_id=sender.id, **message)
        except ValueError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            raise WebSocketException(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, "Invalid JSON")

        chat = await self.chat_repository.get_by_uid_and_member(data.chat_uid, data.sender_id)

        if not chat:
            logger.info(f"Recieve message: chat with UID: {data.chat_uid} not found")
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Chat not found")

        if data.file:
            file_size = calculate_file_size_from_bytes_representation(
                data.file.content.encode("utf-8")
            )

            # getting fresh user data
            user = await self.user_repository.get_by("id", sender.id)

            if not user:
                raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "User not found")

            if not is_available_user_quota_for_file(user.files_mb, file_size):
                self.message_send = None
                await self.answer_error_message(
                    "Превышен максимальный размер загруженных файлов"
                    f"для пользователя({USER_FILES_QUOTA_MB}МБ)"
                )
                return

            file_url = await FileMessageCreator(self.file_storage, data.file).create(chat.uid)

            await self.user_repository.increment_files_mb(sender.id, file_size)

            representation_file_url = await self.file_storage.get_object_url(file_url)

            send_file = SendFile(
                name=data.file.filename,
                url=representation_file_url,
                type=get_file_type(data.file.filename),
            )
        else:
            send_file = None
            file_url = None

        send_message = SendMessage(
            chat_uid=data.chat_uid, sender_id=data.sender_id, text=data.text, file=send_file
        )

        self._set_message_send(send_message)

        await save_new_chat_message_in_db.kiq(chat.id, data.sender_id, data.text, file=file_url)

    def _set_message_send(self, message: SendMessage) -> None:
        """Установить сообщение для последующей отправки."""
        self.message_send = message

    def _set_chat(self, chat: Chat) -> None:
        """Установить чат."""
        self.chat = chat

    def _add_connection(self, chat_uid: UUID) -> None:
        """Добавить соединение к чату."""
        if chat_uid not in WS_CHAT_CONNECTIONS:
            WS_CHAT_CONNECTIONS[chat_uid] = {self.websocket}
        else:
            WS_CHAT_CONNECTIONS[chat_uid].add(self.websocket)

    def disconnect(self) -> None:
        """Отключиться от чата."""
        if self.chat_uid:
            chat = WS_CHAT_CONNECTIONS[self.chat_uid]
            chat.remove(self.websocket)

            if not chat:
                del WS_CHAT_CONNECTIONS[self.chat_uid]
