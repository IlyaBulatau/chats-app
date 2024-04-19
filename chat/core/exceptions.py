class CustomException(Exception):
    message = None

    def __init__(self, message=None, *args, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = self.message or message
        self.field = field


class InCorrectUsername(CustomException):
    pass

class InCorrectPassword(CustomException):
    pass

class MismatchPassword(CustomException):
    pass

class EmptyField(CustomException):
    message = "Поле не может быть пустым"

class AccountNotExists(CustomException):
    message = "Аккаунт не найден"
    