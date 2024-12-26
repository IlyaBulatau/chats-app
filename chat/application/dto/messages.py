from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.dto.files import FileReadDTO


@dataclass(frozen=True, slots=True)
class MessageReadDTO:
    id: int
    uid: UUID
    chat_id: int
    sender_id: int
    created_at: datetime
    text: str | None = None
    file: FileReadDTO | None = None
