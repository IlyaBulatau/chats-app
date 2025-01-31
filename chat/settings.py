from pathlib import Path
from uuid import UUID

from fastapi import WebSocket
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).parent


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_", env_file=BASE_DIR.joinpath(".env"), extra="ignore"
    )

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
    model_config = SettingsConfigDict(env_prefix="GOOGLE_", extra="ignore", env_file=".env")

    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    userinfo_uri: str
    redirect_uri: str
    scope: str


GOOGLE_OAUTH_SETTINGS = GoogleOAuthSettings()


class BrokerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BROKER_", env_file=".env", extra="ignore")

    host: str
    port: int
    username: str
    password: str

    @property
    def dsn(self) -> str:
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}"


BROKER_SETTINGS = BrokerSettings()


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="S3_", env_file=".env", extra="ignore")

    url: str
    bucket: str
    access_key: str
    secret_key: str
    region: str


S3_SETTINGS = S3Settings()

WS_CHAT_CONNECTIONS: dict[UUID, set[WebSocket]] = {}


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_allow_origins: list[str] = ["*"]
    debug: bool = False

    database: DatabaseSettings = DB_SETTINGS
    session: SessionSettings = SESSION_SETTINGS
    google_oauth: GoogleOAuthSettings = GOOGLE_OAUTH_SETTINGS
    broker: BrokerSettings = BROKER_SETTINGS
    s3: S3Settings = S3_SETTINGS


APP_SETTINGS = AppSettings()
