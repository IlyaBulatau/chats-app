from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WebSocketChatEvent:
    NEW_MESSAGE = "new_message"
    DELETE_MESSAGE = "delete_message"
