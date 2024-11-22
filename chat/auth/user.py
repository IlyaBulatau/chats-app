from fastapi.requests import Request
from fastapi.responses import Response
from infrastructure.repositories.users import UserRepository
from jwt.exceptions import DecodeError

from auth.forms import AuthorizationForm, RegisterForm
from auth.password import hash_password, verify_password
from auth.session import Payload, Session
from core.domains import User
from core.exceptions import AccountNotExists, InCorrectPassword, IsExistsUser
from settings import SESSION_SETTINGS


class Registration:
    def __init__(self, registry_user: RegisterForm, user_repository: UserRepository):
        self.registry_form: RegisterForm = registry_user
        self.user_repository: UserRepository = user_repository

    async def __call__(self, *args, **kwargs):
        if await self.is_user_exist(self.registry_form.email):
            raise IsExistsUser(field="email")

        await self.save_user()

    async def save_user(self) -> None:
        form_data = self.registry_form

        await self.user_repository.add(
            username=form_data.username,
            email=form_data.email,
            password=hash_password(form_data.password1),
        )

    async def is_user_exist(self, email: str) -> bool:
        user = await self.user_repository.get_by_email(email=email)

        if user:
            return True

        return False


class Authorization:
    def __init__(
        self,
        authorization_form: AuthorizationForm,
        response: Response,
        user_repository: UserRepository,
    ):
        self.authorization_form: AuthorizationForm = authorization_form
        self.response: Response = response
        self.user_repository: UserRepository = user_repository

    async def __call__(self, *args, **kwargs) -> None:
        user: User | None = await self.user_repository.get_by_email(email=self.authorization_form.email)

        if not user:
            raise AccountNotExists(field="email")

        if not user.password or not verify_password(self.authorization_form.password, user.password):
            raise InCorrectPassword("Не верный пароль", field="password")

        payload: Payload = Payload.for_session(user.id)

        Session().set_cookie(self.response, payload)


async def current_user(request: Request) -> User | None:
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

    from infrastructure.databases import database

    async with database.get_connection() as conn:
        user_repository = UserRepository(conn)
        user: User | None = await user_repository.get_by_id(id_=payload.user_id)

    if not user:
        return None

    return user


async def is_authenticated(request: Request) -> bool:
    user = await current_user(request)

    if not user:
        return False

    return True


def user_logout(response: Response):
    response.delete_cookie(SESSION_SETTINGS.auth_key)
