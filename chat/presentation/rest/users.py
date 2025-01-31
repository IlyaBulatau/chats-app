from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from application.users.services import UserReader
from containers import Container
from core.domains import User
from presentation.rest.dependencies import get_current_user_api
from presentation.rest.representations import success_representation
from presentation.rest.schemas.response import ExceptionResponseSchema, ReceiveUsersResponseSchema


router = APIRouter(prefix="/api/v1/users", tags=["Пользователи"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получение списка пользователей",
    response_description="Возвращает список всех пользователей в системе.",
    responses={
        200: {"model": ReceiveUsersResponseSchema},
        401: {"model": None},
        403: {
            "model": ExceptionResponseSchema,
            "description": "Bad Request.  Возвращает название ошибки с ее описанием.",
        },
    },
)
@inject
async def get_users(
    current_user: User = Depends(get_current_user_api),  # noqa: ARG001
    user_reader: UserReader = Depends(Provide[Container.user_reader]),
):
    users = await user_reader.get_all()

    return success_representation(
        [
            {
                "username": user.username,
                "id": user.id,
            }
            for user in users
        ]
    )
