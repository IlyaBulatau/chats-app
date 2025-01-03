from core.domains import Chat, Message, User


def is_chat_member(member: User, chat: Chat) -> bool:
    """Проверить, что пользователь является участником чата."""
    return member.id in (chat.creator_id, chat.companion_id)


def is_message_sender(sender: User, message: Message) -> bool:
    """Проверить, что пользователь является автором сообщения."""
    return sender.id == message.sender_id
