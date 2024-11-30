from fastapi import status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from settings import BASE_DIR


templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


async def http_not_found_handler(request: Request, *args, **kwargs):
    return templates.TemplateResponse(
        request, name="404.html", status_code=status.HTTP_404_NOT_FOUND
    )


async def http_unauthorized_handler(request: Request, *args, **kwargs):
    return RedirectResponse(request.url_for("authorization_page"))
