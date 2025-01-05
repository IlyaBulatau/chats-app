from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse

from core.exceptions import CustomException
from presentation.rest.schemas.response import ExceptionResponseSchema, SuccessResponseSchema


def exception_representation(
    exc: CustomException, status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Преобразование исключения валидации полей в ошибочный JSON-ответ."""
    if exc.field:
        return JSONResponse(
            ExceptionResponseSchema(
                error=exc.__class__.__name__, result={exc.field: exc.message}
            ).model_dump(),
            status_code=status_code,
        )
    return JSONResponse(
        ExceptionResponseSchema(
            error=exc.__class__.__name__, result={"message": exc.message}
        ).model_dump(),
        status_code=status_code,
    )


def success_representation(data: Any = None, stauts_code: int = status.HTTP_200_OK) -> JSONResponse:
    """Преобразование валидации полей в успешный JSON-ответ."""
    return JSONResponse(
        SuccessResponseSchema(result=data).model_dump(mode="json"), status_code=stauts_code
    )
