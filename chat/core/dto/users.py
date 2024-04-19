from interfaces.dto import BaseDTO


class UserRegistryDTO(BaseDTO):
    username: str
    password: str