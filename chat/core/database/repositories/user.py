from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from interfaces.repository import BaseRepository
from core.domains import User
from core.dto.users import UserRegistryDTO


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def add(cls, session: AsyncSession, user: UserRegistryDTO) -> User:
        smtp = insert(cls.model).values(user.model_dump()).returning(cls.model)

        result = await session.execute(smtp)
        created_user: User = result.scalar()

        return created_user
    
    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> User | None:
        smtp = select(cls.model).filter_by(**kwargs)

        result = await session.execute(smtp)
        user: User = result.scalar()

        if not user:
            return None
    
        return user