class CustomException(Exception):  # noqa: N818
    message: str | None = None

    def __init__(self, message: str | None = None, *args, field: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = self.message or message
        self.field = field


class InCorrectUsername(CustomException):
    pass


class InCorrectPassword(CustomException):
    pass


class MismatchPassword(CustomException):
    pass


class InCorrectEmail(CustomException):
    message = "Не валидный email"


class EmptyField(CustomException):
    message = "Поле не может быть пустым"


class AccountNotExists(CustomException):
    message = "Аккаунт не найден"


class IsExistsUser(CustomException):
    message = "Пользователь уже существует"


class CompanionNotExists(CustomException):
    message = "Собеседник не найден"


class ChatNotFound(CustomException):
    message = "Чат не найден"


class IsNotChatMember(CustomException):
    message = "Вы не являетесь участником чата"
