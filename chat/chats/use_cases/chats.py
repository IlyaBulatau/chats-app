from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.connect import get_db
from core.database.repositories.chat import ChatRepository
from core.domains import Chat


async def get_chats_list(
    db_session: AsyncSession = Depends(get_db), chat_repository: ChatRepository = Depends(ChatRepository)
) -> list[Chat]:
    """Get all chats"""

    return await chat_repository.get_all(db_session)


async def get_chats_by_id(
    chat_id: int, db_session: AsyncSession = Depends(get_db), chat_repository: ChatRepository = Depends(ChatRepository)
) -> Chat:
    """Get all info about chat by id"""

    chat: Chat | None = await chat_repository.get_with_related(db_session, id=chat_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat
