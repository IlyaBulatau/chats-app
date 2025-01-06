from core.domains import Message, User


def is_message_sender(sender: User, message: Message) -> bool:
    """Проверить, что пользователь является автором сообщения."""
    return sender.id == message.sender_id
