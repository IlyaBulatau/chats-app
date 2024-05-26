from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.domains import Chat, Message
from core.dto.chats import ChatCreate
from interfaces.repository import BaseRepository


class ChatRepository(BaseRepository):
    model = Chat

    @classmethod
    async def add(cls, session: AsyncSession, chat: ChatCreate) -> Chat:
        smtp = insert(cls.model).values(**chat.model_dump()).returning(cls.model)

        result = await session.execute(smtp)
        created_chat: Chat = result.scalar()

        return created_chat

    @classmethod
    async def get(cls, session: AsyncSession, **filters) -> Chat | None:
        smtp = select(cls.model).filter_by(**filters)

        result = await session.execute(smtp)
        chat: Chat = result.scalar()

        return chat if chat else None

    @classmethod
    async def get_with_related(cls, session: AsyncSession, **filters) -> Chat | None:
        smtp = (
            select(cls.model)
            .filter_by(**filters)
            .options(joinedload(cls.model.messages).options(joinedload(Message.user)))
        )

        result = await session.execute(smtp)
        chat: Chat = result.scalar()

        return chat if chat else None

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Chat] | None:
        smtp = select(cls.model)

        result = await session.execute(smtp)
        chats: list[Chat] = result.scalars().all()

        return chats
