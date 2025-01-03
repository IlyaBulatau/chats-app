from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    id: int
    username: str
    email: str
    password: str | None = None
    files_mb: Decimal = Decimal(0).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)


@dataclass(frozen=True, slots=True)
class Chat:
    id: int
    uid: UUID
    creator_id: int
    companion_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class Message:
    id: int
    uid: UUID
    chat_id: int
    sender_id: int
    created_at: datetime
    text: str | None = None
    file: str | None = None
