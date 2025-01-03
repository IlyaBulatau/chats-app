from typing import TypedDict
from uuid import UUID


class FileData:
    filename: str
    content: str


class NewMessageData(TypedDict):
    event: str
    chat_uid: UUID | None
    text: str | None
    file: FileData | None
    message_uid: UUID | None
