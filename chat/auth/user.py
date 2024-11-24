from fastapi.requests import Request
from fastapi.responses import Response
from jwt.exceptions import DecodeError

from auth.forms import AuthorizationForm, RegisterForm
from auth.password import hash_password, verify_password
from auth.session import Payload, Session
from core.domains import User
from core.exceptions import AccountNotExists, InCorrectPassword, IsExistsUser
from infrastructure.databases import database
from infrastructure.repositories.users import UserRepository
from settings import SESSION_SETTINGS


class Registration:
    """Сервис отвечающий за процесс регистрации."""

    def __init__(self, registry_user: RegisterForm, user_repository: UserRepository) -> None:
        """
        :param `RegisterForm` registry_user: Обьект формы регистрации с данными пользователя.

        :param `UserRepository` user_repository: Репозиторий пользователей.
        """
        self.registry_form: RegisterForm = registry_user
        self.user_repository: UserRepository = user_repository

    async def __call__(self, *args, **kwargs) -> None:
        """Запуск процесса регистрации."""
        if await self.is_user_exist(self.registry_form.email):
            raise IsExistsUser(field="email")

        await self.save_user()

    async def save_user(self) -> None:
        """Сохраняет пользователя в базе данных."""
        form_data = self.registry_form

        await self.user_repository.add(
            username=form_data.username,
            email=form_data.email,
            password=hash_password(form_data.password1),
        )

    async def is_user_exist(self, email: str) -> bool:
        """Проверяет существует ли пользователь по email полю.

        :param str email: Email из формы регистрации.

        :return bool: True если пользователь существует.
        """
        user = await self.user_repository.get_by("email", email)

        if user:
            return True

        return False


class Authorization:
    """Сервис отвечает за процесс авторизации пользователя."""

    def __init__(
        self,
        authorization_form: AuthorizationForm,
        response: Response,
        user_repository: UserRepository,
    ):
        """
        :param `AuthorizationForm` authorization_form: Форма логина с данными пользователя.

        :param `Response` response: Обьект http ответа.

        :param `UserRepository` user_repository: Репозиторий пользователей.
        """
        self.authorization_form: AuthorizationForm = authorization_form
        self.response: Response = response
        self.user_repository: UserRepository = user_repository

    async def __call__(self, *args, **kwargs) -> None:
        """Запускает процесс авторизации пользователя."""
        user: User | None = await self.user_repository.get_by(
            "email", self.authorization_form.email
        )

        if not user:
            raise AccountNotExists(field="email")

        if not user.password or not verify_password(
            self.authorization_form.password, user.password
        ):
            raise InCorrectPassword("Не верный пароль", field="password")

        payload: Payload = Payload.for_session(user.id)

        Session().set_cookie(self.response, payload)


async def current_user(request: Request) -> User | None:
    """Получить текущего пользователя из обьекта запроса.

    :param `Request` request: Обьект запроса.

    :return `User` | None: DTO пользователя если пользователь найден в базе.
    """
    session_key = request.cookies.get(SESSION_SETTINGS.auth_key)
    session = Session()

    if not session_key:
        return None

    try:
        # invalid session key
        payload: Payload = session.get_payload(session_key)
    except DecodeError:
        return None

    if session.is_expired(payload):
        return None

    async with database.get_connection() as conn:
        user_repository = UserRepository(conn)
        user: User | None = await user_repository.get_by("id", payload.user_id)

    if not user:
        return None

    return user


async def is_authenticated(request: Request) -> bool:
    """Проверка является ли текущий пользователь авторизованным.

    :param `Request` request: Обьект запроса.

    :return bool: True если пользователь является авторизованным.
    """
    user = await current_user(request)

    if not user:
        return False

    return True


def user_logout(response: Response):
    """Удаляет куки из http ответа пользователя, что приводит в выходу из аккаунта.

    :param `Response` response: Обьект http ответа.
    """
    response.delete_cookie(SESSION_SETTINGS.auth_key)
