from pydantic import BaseModel


class SuccessResponseSchema(BaseModel):
    """Схема успешного ответа."""

    success: bool = True


class ExceptionResponseSchema(BaseModel):
    """Схема исключения."""

    success: bool = False
    error: str
    detail: dict[str, str]


class ReceiveMeSchema(BaseModel):
    """Схема получения информации о себе."""

    id: int
    username: str
    email: str
    files_mb: float
