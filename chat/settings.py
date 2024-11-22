from pathlib import Path
from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).parent


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=BASE_DIR.joinpath(".env"), extra="ignore")

    host: str
    port: int = 5432
    login: str
    password: str
    name: str

    @property
    def dsn(self) -> str:
        return "postgresql://{login}:{password}@{host}:{port}/{name}".format(
            login=self.login, password=self.password, host=self.host, port=self.port, name=self.name
        )


DB_SETTINGS = DatabaseSettings()


class SessionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SESSION_", env_file=".env", extra="ignore")

    auth_key: str = "sessionid"
    ttl: int = 60 * 10_080  # неделя
    algorithm: str = "HS256"
    secret: str = "secret"


SESSION_SETTINGS = SessionSettings()


class GoogleOAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(json_file=BASE_DIR.joinpath("googleCreds.json"), extra="ignore")

    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    userinfo_uri: str
    redirect_uri: str
    scope: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            env_settings,
            file_secret_settings,
        )


GOOGLE_OAUTH_SETTINGS = GoogleOAuthSettings()
