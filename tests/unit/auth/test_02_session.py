from datetime import datetime, timedelta

import pytest
from fastapi import Response

from chat.auth.session import Session, Payload
from chat.core.utils import dt_to_str
from chat.settings import SESSION_SETTINGS


@pytest.mark.parametrize("payload", [
    Payload(user_id=10, timestamp=datetime.now()+timedelta(seconds=5)),
    Payload(user_id=1, timestamp=datetime.now()+timedelta(days=1500)),
    Payload(user_id=389, timestamp=datetime.now()),
])
class TestAuthSession:

    
    def test_getting_payload_from_generated_token(self, payload: Payload):
        """Полезная нагрузка берется валидная из сгенерированного токена"""
        session = Session()
        token: str = session._generate_session_token(payload)
        payload_from_token = session.get_payload(token)

        assert dt_to_str(payload.timestamp) == dt_to_str(payload_from_token.timestamp)
        assert payload.user_id == payload_from_token.user_id

    def test_set_cookie_to_response(self, payload):
        session = Session()
        response = Response()
        session.set_cookie(response, payload)

        cookie: bytes = response.raw_headers[1][1]
        key, token = cookie.decode().split("=", 1)

        assert key == SESSION_SETTINGS.auth_key

        # remove - Path from end, remove - ;
        prepare_token = token.split(" ", 1)[0][:-1]
        assert prepare_token == session._generate_session_token(payload)