from fastapi.responses import Response

from auth.oauth.dto import UserOAuthData
from auth.session import Payload, Session
from core.domains import User


class OAuthLogin:
    """Авторизация/Аутентификация через сторонние сервисы"""

    def __init__(
        self,
        user_data: UserOAuthData,
        response: Response,
    ):
        self.user_data: UserOAuthData = user_data
        self.response: Response = response

    async def __call__(self):
        user: User = await self.user_repository.get_by_email(email=self.user_data.email)

        if not user:
            user = await self.user_repository.add(username=self.user_data.username, email=self.user_data.email)

        session = Session()
        payload: Payload = Payload.for_session(user.id)
        session.set_cookie(self.response, payload)
