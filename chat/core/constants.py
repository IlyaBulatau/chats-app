from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokerExchange:
    APP = "app"


@dataclass(frozen=True, slots=True)
class BrokerQueue:
    MESSAGES = "messages"


@dataclass(frozen=True, slots=True)
class StorageDirectory:
    MESSAGE = "messages/chat-{chat_uid}"


USERNAME_LENGHT = 50
CHAT_NAME_LENGHT = 50
MESSAGE_LENGHT = 1000
