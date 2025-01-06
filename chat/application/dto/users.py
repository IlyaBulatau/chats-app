from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserOAuthCreateDTO:
    username: str
    email: str


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: int
    username: str
    email: str
