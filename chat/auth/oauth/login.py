from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from auth.oauth.dto import UserOAuthData
from auth.session import Payload, Session
from core.database.repositories.user import UserRepository
from core.domains import User
from core.dto.users import UserRegistryDTO


class OAuthLogin:
    """Авторизация/Аутентификация через сторонние сервисы"""

    def __init__(
        self, user_data: UserOAuthData, response: Response, user_repository: UserRepository, db_session: AsyncSession
    ):
        self.user_data: UserOAuthData = user_data
        self.response: Response = response
        self.user_repository: UserRepository = user_repository
        self.db_session: AsyncSession = db_session

    async def __call__(self):
        user: User = await self.user_repository.get(self.db_session, email=self.user_data.email)

        if not user:
            user_dto = UserRegistryDTO(username=self.user_data.username, email=self.user_data.email)
            user = await self.user_repository.add(self.db_session, user_dto)
            await self.db_session.commit()

        session = Session()
        payload: Payload = Payload.for_session(user.id)
        session.set_cookie(self.response, payload)
