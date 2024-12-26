from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from fastapi import Response
import jwt

from settings import SESSION_SETTINGS
from shared.datetime_work import dt_to_str, str_to_dt


class Session:
    def set_cookie(self, response: Response, payload: "Payload") -> None:
        """Установить куки в http ответ.

        :param `Response` response: Обьект http ответа.

        :param `Payload` payload: Обьект данных пользователя с полезной нагрузкой.

        :return None:
        """
        response.set_cookie(SESSION_SETTINGS.auth_key, self._generate_session_token(payload))

    def _generate_session_token(self, payload: "Payload") -> str:
        """Сгенерировать JWT токен из данных пользователя и полезной нагрузки.

        :param `Payload` payload: Данные пользователя и полезная нагрузка.

        :return str: Токен JWT.
        """
        payload_dict = payload.to_dict()
        payload_dict["timestamp"] = dt_to_str(payload_dict["timestamp"])
        return jwt.encode(
            payload=payload_dict, key=SESSION_SETTINGS.secret, algorithm=SESSION_SETTINGS.algorithm
        )

    def get_payload(self, token: str) -> "Payload":
        """Получить полезную нагрузку и данные пользователя из JWT токена.

        :param str token: JWT токен.

        :return `Payload`: Данные пользователя и полезная нагрузка.
        """
        payload = jwt.decode(
            token, key=SESSION_SETTINGS.secret, algorithms=[SESSION_SETTINGS.algorithm]
        )
        return Payload(user_id=payload["user_id"], timestamp=str_to_dt(payload["timestamp"]))

    @classmethod
    def is_expired(cls, payload: "Payload") -> bool:
        """Является ли дата из полезной нагрузки просроченной.

        :param `Payload` payload: Полезная нагрузка.

        :return bool: True если дата в прошлом.
        """
        return payload.timestamp < datetime.now()


@dataclass
class Payload:
    user_id: int
    timestamp: datetime  # forever only datetime

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def for_session(cls, user_id: int) -> "Payload":
        """Сгенерировать обьект `Payload` для сесси.

        :param int user_id: ID пользователя.

        :return `Payload`: Обьект `Payload` с данными пользователя и полезной нагрузкой.
        """
        dt = datetime.now() + timedelta(minutes=SESSION_SETTINGS.ttl)
        return cls(user_id=user_id, timestamp=dt)
