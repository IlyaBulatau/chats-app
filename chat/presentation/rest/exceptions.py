from fastapi import status
from fastapi.responses import JSONResponse

from core.exceptions import CustomException
from presentation.rest.schemas import ExceptionResponseSchema


class APINotFoundError(Exception):
    pass


class APIUnauthorizedError(Exception):
    pass


def exception_representation(
    exc: CustomException, status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Преобразование исключения валидации полей в ошибочный JSON-ответ."""
    return JSONResponse(
        ExceptionResponseSchema(
            error=exc.__class__.__name__, detail={exc.field: exc.message}
        ).model_dump(),
        status_code=status_code,
    )
