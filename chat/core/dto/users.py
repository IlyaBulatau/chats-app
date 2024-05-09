from interfaces.dto import BaseDTO


class UserRegistryDTO(BaseDTO):
    username: str
    email: str
    password: str | None = None
