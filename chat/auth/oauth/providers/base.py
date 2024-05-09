from abc import ABC, abstractmethod

from pydantic_settings import BaseSettings

from auth.oauth.dto import UserOAuthData


class BaseOAuthProdiver(ABC):
    settings: BaseSettings = None

    @classmethod
    @abstractmethod
    def get_oauth_url(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    async def login(cls) -> UserOAuthData:
        pass
