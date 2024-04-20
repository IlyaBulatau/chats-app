import pytest
from fastapi import Response

from chat.auth import user as auth_user
from chat.core.database.repositories.user import UserRepository
from chat.settings import SESSION_SETTINGS
from core.exceptions import AccountNotExists # type: ignore


class TestAuthorizationProcess:

    async def test_authorization_positive(self, user_factory, db_session, monkeypatch):
        """Успшеная автораизации - факт наличия куки"""
        monkeypatch.setattr(auth_user, "verify_password", lambda *args, **kwargs: True)
        
        user = await user_factory()
        response = Response()
        user_repo = UserRepository()
        
        auth = auth_user.Authorization(user, response, user_repo, db_session)
        await auth()

        cookie: bytes = response.raw_headers[1][1]
        key, token = cookie.decode().split("=", 1)

        assert key == SESSION_SETTINGS.auth_key
        assert token is not None
    

    async def test_user_not_found(self, user_factory, db_session, monkeypatch):
        """Авторизация под не зарегистрированным пользователем"""
        monkeypatch.setattr(auth_user, "verify_password", lambda *args, **kwargs: True)

        user = user_factory.build()
        response = Response()
        user_repo = UserRepository()
        auth = auth_user.Authorization(user, response, user_repo, db_session)
        
        with pytest.raises(AccountNotExists) as exc:
            await auth()

        assert exc.value.message == "Аккаунт не найден"
        assert exc.value.field == "username"
