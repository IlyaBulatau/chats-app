from abc import ABC, abstractmethod
import logging

from application.chats import exceptions
from application.chats.schemas import NewMessageData
from application.chats.services.messages import MessageCreator, MessageRemover
from application.chats.validators import DeleteMessage, ReceivedMessage, SendMessage
from core.domains import User


logger = logging.getLogger("uvicorn")


class BaseMessageHandler(ABC):
    @abstractmethod
    async def handle(self, message: NewMessageData): ...


class NewMessageHandler(BaseMessageHandler):
    """Создает новое сообщение в чате."""

    def __init__(
        self,
        message_creator: MessageCreator,
        sender: User,
    ):
        self.message_creator = message_creator
        self.sender = sender

    async def handle(self, message: NewMessageData) -> SendMessage:
        """
        Валиация сообщения, сохранение.

        :param `NewMessageData` message: Данные сообщения.

        :return: `SendMessage`
        """
        try:
            data = ReceivedMessage(sender_id=self.sender.id, **message)
        except ValueError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            raise exceptions.InvalidJsonDataError("Invalid json message")

        return await self.message_creator.create(**data.model_dump())


class DeleteMessageHandler(BaseMessageHandler):
    """Удаляет сообщение из чата."""

    def __init__(
        self,
        message_remover: MessageRemover,
        sender: User,
    ):
        self.sender = sender
        self.message_remover = message_remover

    async def handle(self, message: NewMessageData) -> None:
        """Удаление сообщения.

        :param `NewMessageData` message: Данные сообщения.

        :return: None
        """
        try:
            data = DeleteMessage(**message)
        except ValueError as exc:
            logger.error("Recieve message: invalid data: %s", exc)
            raise exceptions.InvalidJsonDataError("Invalid json message")

        await self.message_remover.remove(data.message_uid, self.sender)
