from core.domains import Chat


async def get_chats_list() -> list[Chat]:
    """Get all chats"""

    return []


async def get_chats_by_id(
    chat_id: int,
) -> Chat:
    """Get all info about chat by id"""

    return chat_id
