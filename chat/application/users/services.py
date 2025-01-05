from core.domains import User
from infrastructure.repositories.users import UserRepository


class UserReader:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_all(self) -> list[User]:
        return await self.user_repository.get_all()
