from datetime import datetime, timedelta

from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from auth.forms import AuthorizationForm, RegisterForm
from auth.password import hash_password, verify_password
from auth.session import Payload, Session
from core.database.repositories.user import UserRepository
from core.domains import User
from core.dto.users import UserRegistryDTO
from core.exceptions import AccountNotExists, InCorrectPassword
from settings import SESSION_SETTINGS


class Registraton:
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
