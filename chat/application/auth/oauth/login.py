import logging

from fastapi.responses import Response

from application.auth.session import Payload, Session
from application.dto.users import UserOAuthCreateDTO
from core.domains import User
from infrastructure.repositories.users import UserRepository


logger = logging.getLogger("uvicorn")


class OAuthLogin:
    """Авторизация/Аутентификация через сторонние сервисы."""

    def __init__(
        self, user_data: UserOAuthCreateDTO, response: Response, user_repository: UserRepository
    ):
        """
        :param `UserOAuthCreateDTO` user_data: Данные пользователя.

        :param `Response` response: Обьект http ответа.

        :param `UserRepository` user_repository: Репозиторий пользователей.
        """
        self.user_data: UserOAuthCreateDTO = user_data
        self.response: Response = response
        self.user_repository = user_repository

    async def __call__(self):
        """Запуск процесса авторизации."""
        user: User | None = await self.user_repository.get_by("email", self.user_data.email)

        if not user:
            user_id = await self.user_repository.add(
                username=self.user_data.username, email=self.user_data.email
            )
            logger.info("OAuthLogin: user with email %s was created", self.user_data.email)
        else:
            user_id = user.id

        session = Session()
        payload: Payload = Payload.for_session(user_id)
        session.set_cookie(self.response, payload)
