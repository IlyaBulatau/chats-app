import logging

from aiohttp import ClientSession
from requests import PreparedRequest

from application.auth.oauth.providers.base import BaseOAuthProdiver
from application.dto.users import UserOAuthCreateDTO
from settings import GOOGLE_OAUTH_SETTINGS


logger = logging.getLogger("uvicorn")


class GoogleOAuthProvider(BaseOAuthProdiver):
    settings = GOOGLE_OAUTH_SETTINGS

    @classmethod
    def get_oauth_url(cls) -> str:
        """Получение ссылки на авторизацию к google сервису.

        :return str: URL от google для ссылки на авторизацию.
        """
        base_url = cls.settings.auth_uri
        params = {
            "client_id": cls.settings.client_id,
            "redirect_uri": cls.settings.redirect_uri,
            "response_type": "code",
            "scope": cls.settings.scope,
        }
        request = PreparedRequest()
        request.prepare_url(base_url, params)
        return request.url

    @classmethod
    async def login(cls, code: str) -> UserOAuthCreateDTO:
        """Получение данных пользователя для логина от google.

        :param str code: Код от коллбек вызова google для логина.

        :return `UserOAuthCreateDTO`: Данные пользователя.
        """
        # TODO: обработать не 200 код
        token = await cls._get_token_for_login(code)

        async with ClientSession(headers={"Authorization": f"Bearer {token}"}) as client:
            async with client.get(cls.settings.userinfo_uri) as response:
                data = await response.json()
                logger.info("OAuthLogin: Request for login: %s", response.status)

                return cls.prepared_data(data)

    @classmethod
    async def _get_token_for_login(cls, auth_code: str) -> str:
        """Получение JWT токена у google для запроса на логин.

        :param str auth_code: Код от коллбека.

        :return str: JWT токен.
        """
        payload = {
            "client_id": cls.settings.client_id,
            "client_secret": cls.settings.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": cls.settings.redirect_uri,
        }
        async with (
            ClientSession() as client,
            client.post(cls.settings.token_uri, data=payload) as response,
        ):
            # TODO: обработать не 200 ответ
            logger.info("OAuthLogin: Request geting jwt token for login: %s", response.status)
            data = await response.json()

            return data.get("access_token")

    @classmethod
    def prepared_data(cls, data: dict) -> UserOAuthCreateDTO:
        """Преобразовать полученные от google данные в обьект `UserOAuthCreateDTO`.

        :param dict data: Данные json пользователя

        :return `UserOAuthCreateDTO`: Данные пользователя в обьекте `UserOAuthCreateDTO`.
        """
        return UserOAuthCreateDTO(username=data.get("name"), email=data.get("email"))  # type: ignore
