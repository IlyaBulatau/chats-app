from typing import TypedDict
from uuid import UUID


class NewMessageData(TypedDict):
    chat_uid: UUID | None
    text: str | None
