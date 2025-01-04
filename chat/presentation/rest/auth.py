from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from application.auth.forms import AuthorizationForm, RegisterForm
from application.auth.user import Authorization, Registration, user_logout
from core.domains import User
from core.exceptions import CustomException
from infrastructure.repositories.users import UserRepository
from presentation.rest.dependencies import get_current_user_api
from presentation.rest.exceptions import exception_representation
from presentation.rest.schemas import (
    ExceptionResponseSchema,
    ReceiveMeSchema,
    SuccessResponseSchema,
)
from shared.dependencies import get_repository


router = APIRouter(prefix="/api/v1/auth", tags=["Авторизация"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация",
    response_description="При успешной регистрации возвращает код 201.",
    responses={
        201: {"model": SuccessResponseSchema},
        400: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
    },
)
async def registration(
    username: str,
    email: str,
    password1: str,
    password2: str,
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Регистрация пользователя"""
    try:
        form = RegisterForm(
            username=username, email=email, password1=password1, password2=password2
        )
        registration_user = Registration(form, user_repository)
        await registration_user()
    except CustomException as exc:
        return exception_representation(exc)

    return JSONResponse(
        content=SuccessResponseSchema().model_dump(), status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/authorization",
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    response_description="При успешном входе в систему устанавливает в куки токен.",
    responses={
        200: {"model": None},
        400: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
    },
)
async def authorization(
    email: str,
    password: str,
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Логин"""
    response = JSONResponse(content=SuccessResponseSchema().model_dump())

    try:
        form = AuthorizationForm(email=email, password=password)
        authorization_user = Authorization(form, response, user_repository)
        await authorization_user()
    except CustomException as exc:
        return exception_representation(exc)

    return response


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
    response_description="Возвращает пустое тело, статус 204.",
    responses={204: {"model": None}, 401: {"model": None}},
)
async def logout_method(
    user: User = Depends(get_current_user_api),  # noqa: ARG001
):
    """Выход из системы"""
    response = JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
    user_logout(response)

    return response


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Получение информации о пользователе",
    response_description="Возвращает информацию о пользователе.",
    responses={200: {"model": ReceiveMeSchema}, 401: {"model": None}},
)
async def get_me(
    user: User = Depends(get_current_user_api),
):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "files_mb": user.files_mb,
    }
