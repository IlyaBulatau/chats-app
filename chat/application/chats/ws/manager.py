import json
from json import JSONDecodeError
import logging
from uuid import UUID

from fastapi import WebSocket, WebSocketException, status

from application.chats import exceptions
from application.chats.schemas import NewMessageData
from application.chats.services.files import FileMessageCreator
from application.chats.services.messages import MessageCreator, MessageRemover
from application.chats.validators import SendMessage
from application.chats.ws.events import WebSocketChatEvent
from application.chats.ws.handlers import (
    BaseMessageHandler,
    DeleteMessageHandler,
    NewMessageHandler,
)
from core.constants import USER_FILES_QUOTA_MB
from core.domains import Chat, User
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.messages import MessageRepository
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
        message_repository: MessageRepository,
        file_storage: FileStorage,
    ):
        """Инициализация менеджера для работы с чатами.

        :param `WebSocket` websocket: Объект WebSocket.

        :param `UUID` chat_uid: Уникальный идентификатор чата.

        :param `User` current_user: Текущий пользователь.

        :param `ChatRepository` chat_repository: Репозиторий чатов.

        :param `UserRepository` user_repository: Репозиторий пользователей.

        :param `MessageRepository` message_repository: Репозиторий сообщений.

        :param `FileStorage` file_storage: Хранилище файлов.
        """
        self.websocket = websocket
        self.chat_uid = chat_uid
        self.current_user = current_user
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.message_repository = message_repository
        self.file_storage = file_storage
        self.message_send: SendMessage | None = None

        self._add_connection(self.chat_uid)

        self.EVENT_HANDLERS: dict[str, BaseMessageHandler] = {
            WebSocketChatEvent.NEW_MESSAGE: NewMessageHandler(
                MessageCreator(
                    user_repository,
                    message_repository,
                    chat_repository,
                    file_storage,
                    FileMessageCreator(file_storage),
                ),
                self.current_user,
            ),
            WebSocketChatEvent.DELETE_MESSAGE: DeleteMessageHandler(
                MessageRemover(message_repository), self.current_user
            ),
        }

    async def receive_message(self) -> None:
        """Получить и обработать сообщение от клиента."""
        try:
            data: NewMessageData = await self.websocket.receive_json()
            handler = self.EVENT_HANDLERS[data["event"]]

            message: SendMessage | None = await handler.handle(data)
            self._set_message_send(message)
        except KeyError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            self.disconnect()
            raise WebSocketException(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, "Invalid JSON")
        except JSONDecodeError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            self.disconnect()
            raise WebSocketException(status.WS_1003_UNSUPPORTED_DATA, "Invalid JSON")
        except exceptions.InvalidJsonDataError:
            self.disconnect()
            raise WebSocketException(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, "Invalid JSON")
        except exceptions.ChatNotFoundError:
            self.disconnect()
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Chat not found")
        except exceptions.MessageNotFoundError:
            self.disconnect()
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Message not found")
        except exceptions.UserNotFoundError:
            self.disconnect()
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "User not found")
        except exceptions.PermissionDeniedDeleteMessageError:
            self.disconnect()
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Permission denied")
        except exceptions.FileQuotaSizeError:
            self._set_message_send(None)
            self.disconnect()
            await self.answer_error_message(
                "Превышен максимальный размер загруженных файлов"
                f"для пользователя({USER_FILES_QUOTA_MB}МБ)"
            )

    async def broadcast_message(self) -> None:
        """Отправить сообщение всем подключенным к чату клиентам."""
        if self.message_send:
            for connection in WS_CHAT_CONNECTIONS[self.chat_uid]:
                await connection.send_text(self.message_send.model_dump_json())

    async def answer_error_message(self, message: str | None) -> None:
        """Отправить сообщение об ошибке клиенту отправившиму сообщение."""
        await self.websocket.send_text(json.dumps({"error": message}))

    def _set_message_send(self, message: SendMessage | None) -> None:
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
            logger.info(
                f"Client ID: {self.current_user.id} disconnected from chat ID: {self.chat_uid}."
            )
            if not chat:
                del WS_CHAT_CONNECTIONS[self.chat_uid]
