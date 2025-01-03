from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class ReceivedFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    filename: str
    content: str


class SendFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    url: str
    type: Literal["image", "file"]


class ReceivedMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chat_uid: UUID
    sender_id: int
    text: str | None = None
    file: ReceivedFile | None = None

    @model_validator(mode="after")
    def valid_text_or_file(self):
        if not self.text and not self.file:
            raise ValueError("Для сообщения отсутствует контент.")

        return self


class SendMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chat_uid: UUID
    sender_id: int
    text: str | None = None
    file: SendFile | None = None

    @model_validator(mode="after")
    def valid_text_or_file(self):
        if not self.text and not self.file:
            raise ValueError("Для сообщения отсутствует контент.")

        return self


class DeleteMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message_uid: UUID
