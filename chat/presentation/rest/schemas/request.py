from pydantic import BaseModel, Field


class RegistrationRequestSchema(BaseModel):
    """Схема запроса регистрации."""

    username: str = Field(description="Имя пользователя")
    email: str = Field(description="Email")
    password1: str = Field(description="Пароль")
    password2: str = Field(description="Подтверждение пароля")


class AuthorizationRequestSchema(BaseModel):
    """Схема запроса авторизации."""

    email: str = Field(description="Email пользователя")
    password: str = Field(description="Пароль")


class CreateChatRequestSchema(BaseModel):
    """Схема запроса создания чата."""

    companion_id: int
