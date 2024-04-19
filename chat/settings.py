from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=BASE_DIR.joinpath(".env"), extra="ignore")

    driver: str = "asyncpg"
    host: str
    port: int = 5432
    login: str
    password: str
    name: str

    @property
    def dsn(self) -> str:
        return "postgresql+asyncpg://{login}:{password}@{host}:{port}/{name}".format(
            login=self.login,
            password=self.password,
            host=self.host,
            port=self.port,
            name=self.name
        )

DB_SETTINGS = DatabaseSettings()


class SessionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SESSION_", env_file=".env", extra="ignore")

    auth_key: str = "sessionid"
    ttl: int = 60*10_080 # неделя
    algorithm: str = "HS256"
    secret: str = "secret"

SESSION_SETTINGS = SessionSettings()