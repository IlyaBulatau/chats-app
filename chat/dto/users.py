from dataclasses import dataclass


@dataclass(frozen=True)
class UserOAuthCreateDTO:
    username: str
    email: str
