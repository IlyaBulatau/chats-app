from dataclasses import dataclass

from core.domains import Chat, User


@dataclass(frozen=True, slots=True)
class ChatInfoDTO:
    chat: Chat
    creator: User
    companion: User
