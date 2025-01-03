from typing import TypedDict
from uuid import UUID


class FileData(TypedDict):
    """Данные файла из сообщения."""

    filename: str
    content: str


class NewMessageData(TypedDict):
    """Данные нового сообщения от клиента."""

    event: str
    chat_uid: UUID | None
    text: str | None
    file: FileData | None
    message_uid: UUID | None
