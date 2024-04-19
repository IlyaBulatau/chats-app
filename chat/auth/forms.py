from pydantic import field_validator, model_validator

from auth.validators import PasswordValidatorField, UsernameValidatorField
from core.exceptions import EmptyField
from interfaces.form import BaseForm


class RegisterForm(BaseForm):
    username: str
    password1: str
    password2: str

    @field_validator("username", mode="before")
    @classmethod
    def username_validate(cls, username: str) -> str:
        if not username:
            raise EmptyField(field="username")
        UsernameValidatorField.validate(username)
        return username

    @model_validator(mode="before")
    @classmethod
    def password_validate(cls, data):
        password1 = data.get("password1")
        password2 = data.get("password2")

        if not (password1 or password2):
            raise EmptyField(field="password")
        PasswordValidatorField.validate(password1)
        PasswordValidatorField.has_match_password(password1, password2)

        return data


class AuthorizationForm(BaseForm):
    username: str
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def username_validate(cls, username: str) -> str:
        if not username:
            raise EmptyField(field="username")
        UsernameValidatorField.validate(username)
        return username

    @field_validator("password", mode="before")
    @classmethod
    def password_validate(cls, password: str) -> str:
        if not password:
            raise EmptyField(field="password")
        return password
