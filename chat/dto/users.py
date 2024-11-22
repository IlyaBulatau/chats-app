from dataclasses import dataclass


@dataclass(frozen=True)
class UserDTO:
    id: int
    username: str
    email: str
    password: str
