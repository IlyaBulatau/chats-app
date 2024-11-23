from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from fastapi import Response
import jwt

from core.utils import dt_to_str, str_to_dt
from settings import SESSION_SETTINGS


class Session:
    def set_cookie(self, response: Response, payload: "Payload") -> None:
        response.set_cookie(SESSION_SETTINGS.auth_key, self._generate_session_token(payload))

    def _generate_session_token(self, payload: "Payload") -> str:
        payload_dict = payload.to_dict()
        payload_dict["timestamp"] = dt_to_str(payload_dict["timestamp"])
        return jwt.encode(
            payload=payload_dict, key=SESSION_SETTINGS.secret, algorithm=SESSION_SETTINGS.algorithm
        )

    def get_payload(self, token: str) -> "Payload":
        payload = jwt.decode(
            token, key=SESSION_SETTINGS.secret, algorithms=[SESSION_SETTINGS.algorithm]
        )
        return Payload(user_id=payload["user_id"], timestamp=str_to_dt(payload["timestamp"]))

    @classmethod
    def is_expired(cls, payload: "Payload") -> bool:
        return payload.timestamp < datetime.now()


@dataclass
class Payload:
    user_id: int
    timestamp: datetime  # forever only datetime

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def for_session(cls, user_id: int) -> "Payload":
        dt = datetime.now() + timedelta(minutes=SESSION_SETTINGS.ttl)
        return cls(user_id=user_id, timestamp=dt)
