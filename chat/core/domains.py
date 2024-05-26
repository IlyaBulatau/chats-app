from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    email: str
    chats: list["Chat"]
    messages: list["Message"]
    password: str | None = None


@dataclass
class Chat:
    id: int
    title: str
    owner_id: int
    users: list["User"]
    messages: list["Message"]


@dataclass
class Message:
    id: int
    text: str
    user_id: int
    chat_id: int
    user: User
    chat: Chat
