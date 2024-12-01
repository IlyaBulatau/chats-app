from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokerExchange:
    APP = "app"


@dataclass(frozen=True, slots=True)
class BrokerQueue:
    MESSAGES = "messages"


USERNAME_LENGHT = 50
CHAT_NAME_LENGHT = 50
MESSAGE_LENGHT = 1000
