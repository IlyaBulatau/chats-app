from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from core.domains import Chat, User


@dataclass(frozen=True, slots=True)
class ChatInfoDTO:
    chat: Chat
    creator: User
    companion: User


@dataclass(frozen=True, slots=True)
class ChatReadDTO:
    id: int
    uid: UUID
    creator_id: int
    companion_id: int
    created_at: datetime
    updated_at: datetime
