from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReceivedMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str
    chat_uid: UUID
    sender_id: int
