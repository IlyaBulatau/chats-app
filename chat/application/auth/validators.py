from core.constants import USERNAME_LENGHT
from core.exceptions import InCorrectPassword, InCorrectUsername, MismatchPassword
from core.validator import BaseValidatorField


class UsernameValidatorField(BaseValidatorField):
    MIN_LENGHT = 3

    @classmethod
    def is_valid_lenght(cls, username: str) -> None:
        if not (cls.MIN_LENGHT < len(username) <= USERNAME_LENGHT):
            raise InCorrectUsername(
                f"Длинна имени должна быть в пределах {cls.MIN_LENGHT}-{USERNAME_LENGHT} символов",
                field="username",
            )

    @classmethod
    def is_string(cls, username) -> None:
        if not isinstance(username, str):
            raise InCorrectUsername("Имя должно быть строковым представлением", field="username")


class PasswordValidatorField(BaseValidatorField):
    MIN_LENGHT = 8

    @classmethod
    def is_valid_lenght(cls, password) -> None:
        if len(password) < cls.MIN_LENGHT:
            raise InCorrectPassword(
                f"Длинна пароля должна быть более {cls.MIN_LENGHT} символов", field="password"
            )

    @classmethod
    def is_have_digit(cls, password) -> None:
        for letter in password:
            if letter.isdigit():
                return
        raise InCorrectPassword("Пароль должен содержать хотя бы 1 цифру", field="password")

    @classmethod
    def is_not_have_space(cls, password) -> None:
        spaces = " \n\t"
        for sy in password:
            if sy in spaces:
                raise InCorrectPassword(
                    "Пароль не должен содержать пробелов и знаков табуляции", field="password"
                )

    @classmethod
    def has_match_password(cls, password1, password2) -> None:
        if not password1 == password2:
            raise MismatchPassword("Пароли не совпадают", field="password")
