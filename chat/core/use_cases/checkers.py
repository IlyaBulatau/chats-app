from core.domains import Chat, User


def is_chat_member(member: User, chat: Chat) -> bool:
    """Проверить, что пользователь является участником чата."""
    return member.id in (chat.creator_id, chat.companion_id)
