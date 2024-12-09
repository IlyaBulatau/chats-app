from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from settings import BASE_DIR


templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


async def http_not_found_handler(request: Request, *args, **kwargs):
    current_user = request.state._state["user"]  # type: ignore # noqa: SLF001

    if current_user:
        return RedirectResponse(request.url_for("index"))

    return RedirectResponse(request.url_for("authorization_page"))


async def http_unauthorized_handler(request: Request, *args, **kwargs):
    return RedirectResponse(request.url_for("authorization_page"))
