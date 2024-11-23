from abc import ABC, abstractmethod
from typing import Protocol

from pydantic_settings import BaseSettings

from dto.users import UserOAuthData


class BaseOAuthProdiver(ABC):
    settings: BaseSettings

    @classmethod
    @abstractmethod
    def get_oauth_url(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    async def login(cls, *args, **kwargs) -> UserOAuthData:
        pass


class Provider(Protocol):
    @classmethod
    def get_oauth_url(cls) -> str:
        pass

    @classmethod
    async def login(cls, *args, **kwargs) -> UserOAuthData:
        pass
