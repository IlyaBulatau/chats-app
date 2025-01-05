from fastapi import APIRouter, Depends, status

from application.users.services import UserReader
from core.domains import User
from infrastructure.repositories.users import UserRepository
from presentation.rest.dependencies import get_current_user_api
from presentation.rest.representations import success_representation
from presentation.rest.schemas.response import ExceptionResponseSchema, ReceiveUsersResponseSchema
from shared.dependencies import get_repository


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
async def get_users(
    current_user: User = Depends(get_current_user_api),  # noqa: ARG001
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    user_reader = UserReader(user_repository)

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
