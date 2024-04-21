from datetime import datetime, timedelta

from fastapi.requests import Request
from fastapi.responses import Response
from jwt.exceptions import DecodeError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.forms import AuthorizationForm, RegisterForm
from auth.password import hash_password, verify_password
from auth.session import Payload, Session
from core.database.connect import get_db
from core.database.repositories.user import UserRepository
from core.domains import User
from core.dto.users import UserRegistryDTO
from core.exceptions import AccountNotExists, InCorrectPassword
from settings import SESSION_SETTINGS


class Registration:
    def __init__(self, registry_user: RegisterForm, user_repository: UserRepository, db_session: AsyncSession):
        self.registry_form: RegisterForm = registry_user
        self.user_repository: UserRepository = user_repository
        self.db_session: AsyncSession = db_session

    async def __call__(self, *args, **kwargs):
        await self.save_user(self.db_session)
        await self.db_session.commit()

    async def save_user(self, session: AsyncSession) -> None:
        form_data = self.registry_form
        user_dto = UserRegistryDTO(username=form_data.username, password=hash_password(form_data.password1))
        await self.user_repository.add(session, user_dto)


class Authorization:
    def __init__(
        self,
        authorization_form: AuthorizationForm,
        response: Response,
        user_repository: UserRepository,
        db_session: AsyncSession,
    ):
        self.authorization_form: AuthorizationForm = authorization_form
        self.response: Response = response
        self.user_repository: UserRepository = user_repository
        self.db_session: AsyncSession = db_session

    async def __call__(self, *args, **kwargs):
        user: User = await self.user_repository.get(self.db_session, username=self.authorization_form.username)
        if not user:
            raise AccountNotExists(field="username")

        if not verify_password(self.authorization_form.password, user.password):
            raise InCorrectPassword("Не верный пароль", field="password")

        payload: Payload = self.generate_payload(user.id)
        Session().set_cookie(self.response, payload)

    def generate_payload(self, user_id: int) -> Payload:
        dt = datetime.now().replace(tzinfo=None) + timedelta(minutes=SESSION_SETTINGS.ttl)
        return Payload(user_id=user_id, timestamp=dt)


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

    async_session = await anext(get_db())
    user_repo = UserRepository()
    user: User | None = await user_repo.get(async_session, id=payload.user_id)

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
