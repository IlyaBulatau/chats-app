from fastapi.requests import Request

from core.domains import User


async def get_current_user(request: Request) -> User | None:
    user: User | None = request.state._state["user"]  # noqa: SLF001
    return user
