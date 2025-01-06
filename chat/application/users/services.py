from application.dto.users import UserDTO
from infrastructure.repositories.users import UserRepository


class UserReader:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_all(self) -> list[UserDTO]:
        users = await self.user_repository.get_all()

        return [UserDTO(id=user.id, username=user.username, email=user.email) for user in users]
