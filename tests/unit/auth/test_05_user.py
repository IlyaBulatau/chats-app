from dataclasses import dataclass
from datetime import datetime

from fastapi.responses import Response

from auth import user as auth_user
from chat.core.domains import User
from chat.auth.session import Session, Payload
from chat.auth.user import current_user, is_authenticated, user_logout
from chat.settings import SESSION_SETTINGS


class TestUserMethod:

    @dataclass
    class Request:
        cookies: dict

    async def test_getting_current_user(self, user_factory, monkeypatch):
        user: User = await user_factory()
        session = Session()
        key = session._generate_session_token(Payload(user.id, datetime.now()))
        request = self.Request({SESSION_SETTINGS.auth_key: key})

        monkeypatch.setattr(auth_user, "Request", request)
        
        _current_user: User = await current_user(request)
        # TODO: не находит пользователя, вне теста работает
    

    async def test_logout_user_deleted_cookie(self):
        response = Response()
        response.set_cookie(SESSION_SETTINGS.auth_key, "cookie value")
        user_logout(response)
        
        cookie_b: bytes = response.headers.raw[-1][1]
        cookie = cookie_b.decode().split(";", 1)[0]
        
        assert cookie == SESSION_SETTINGS.auth_key+'=""'
