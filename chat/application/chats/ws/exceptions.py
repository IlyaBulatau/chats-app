class InvalidJsonDataError(Exception):
    pass


class ChatNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class FileQuotaSizeError(Exception):
    pass


class MessageNotFoundError(Exception):
    pass


class PermissionDeniedDeleteMessageError(Exception):
    pass
