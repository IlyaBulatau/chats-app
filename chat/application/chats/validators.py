from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class ReceivedFile(BaseModel):
    """Данные полученного файлового сообщения от клиента."""

    model_config = ConfigDict(extra="ignore")

    filename: str
    content: str


class SendFile(BaseModel):
    """Данные отправляемого файлового сообщения для клиента."""

    model_config = ConfigDict(extra="ignore")

    name: str
    url: str
    type: Literal["image", "file"]


class ReceivedMessage(BaseModel):
    """Данные полученного сообщения от клиента."""

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
    """Данные отправляемого сообщения для клиента."""

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
    """Данные полученного сообщения от клиента для удаления сообщения."""

    model_config = ConfigDict(extra="ignore")

    message_uid: UUID
