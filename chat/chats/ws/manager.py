from json import JSONDecodeError
import logging
from uuid import UUID

from fastapi import WebSocket, WebSocketException, status

from backgroud_tasks.tasks import save_new_chat_message_in_db
from chats.services.files import FileMessageCreator
from chats.ws.schemas import NewMessageData
from chats.ws.validators import ReceivedMessage
from core.domains import Chat, User
from infrastructure.repositories.chats import ChatRepository
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
    ):
        """Инициализация менеджера для работы с чатами.

        :param `WebSocket` websocket: Объект WebSocket.

        :param `UUID` chat_uid: Уникальный идентификатор чата.

        :param `User` current_user: Текущий пользователь.

        :param `ChatRepository` chat_repository: Репозиторий чатов.
        """
        self.websocket = websocket
        self.chat_uid = chat_uid
        self.current_user = current_user
        self.chat_repository = chat_repository
        self.last_received_message: ReceivedMessage | None = None

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
        if self.last_received_message:
            for connection in WS_CHAT_CONNECTIONS[self.chat_uid]:
                await connection.send_text(self.last_received_message.model_dump_json())

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
            file_url = await FileMessageCreator(FileStorage(), data.file).create(chat.uid)
        else:
            file_url = None

        self._set_last_received_message(data)

        await save_new_chat_message_in_db.kiq(chat.id, data.sender_id, data.text, file=file_url)

    def _set_last_received_message(self, message: ReceivedMessage) -> None:
        """Установить последнее полученное сообщение."""
        self.last_received_message = message

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
