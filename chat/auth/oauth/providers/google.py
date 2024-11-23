from aiohttp import ClientSession
from requests import PreparedRequest

from auth.oauth.providers.base import BaseOAuthProdiver
from dto.users import UserOAuthData
from settings import GOOGLE_OAUTH_SETTINGS


class GoogleOAuthProvider(BaseOAuthProdiver):
    settings = GOOGLE_OAUTH_SETTINGS

    @classmethod
    def get_oauth_url(cls) -> str:
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
    async def login(cls, code: str) -> UserOAuthData:
        # TODO: обработать не 200 код
        token = await cls._get_token_for_login(code)

        async with ClientSession(headers={"Authorization": f"Bearer {token}"}) as client:
            async with client.get(cls.settings.userinfo_uri) as response:
                data = await response.json()
                return cls.prepared_data(data)

    @classmethod
    async def _get_token_for_login(cls, auth_code: str) -> str:
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
            data = await response.json()
            return data.get("access_token")

    @classmethod
    def prepared_data(cls, data: dict) -> UserOAuthData:
        return UserOAuthData(username=data.get("name"), email=data.get("email"))  # type: ignore
