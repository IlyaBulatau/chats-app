from fastapi.responses import Response

from auth.session import Payload, Session
from dto.users import UserDTO, UserOAuthData
from infrastructure.repositories.users import UserRepository


class OAuthLogin:
    """Авторизация/Аутентификация через сторонние сервисы"""

    def __init__(
        self, user_data: UserOAuthData, response: Response, user_repository: UserRepository
    ):
        self.user_data: UserOAuthData = user_data
        self.response: Response = response
        self.user_repository = user_repository

    async def __call__(self):
        user: UserDTO | None = await self.user_repository.get_by_email(email=self.user_data.email)

        if not user:
            user_id = await self.user_repository.add(
                username=self.user_data.username, email=self.user_data.email
            )
        else:
            user_id = user.id

        session = Session()
        payload: Payload = Payload.for_session(user_id)
        session.set_cookie(self.response, payload)
