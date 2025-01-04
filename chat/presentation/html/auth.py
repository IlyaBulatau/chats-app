from fastapi import APIRouter, Depends, Form, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from application.auth.forms import AuthorizationForm, RegisterForm
from application.auth.oauth.constants import Providers
from application.auth.oauth.dispatch import get_oauth_provider
from application.auth.oauth.login import OAuthLogin
from application.auth.oauth.providers.base import Provider
from application.auth.user import Authorization, Registration, user_logout
from application.dto.users import UserOAuthCreateDTO
from core.domains import User
from core.exceptions import CustomException
from infrastructure.repositories.users import UserRepository
from presentation.html.dependencies import get_current_user
from settings import BASE_DIR
from shared.dependencies import get_repository


router = APIRouter(prefix="/auth", include_in_schema=False)
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Получение страницы для регистрации"""
    return templates.TemplateResponse(request=request, name="register.html")


@router.get("/authorization", response_class=HTMLResponse)
async def authorization_page(request: Request):
    """Получение страницы для логина"""
    return templates.TemplateResponse(request=request, name="authorization.html")


@router.post("/register", response_class=HTMLResponse)
async def register_method(
    request: Request,
    username: str | None = Form(None, description="Имя пользователя"),
    email: str | None = Form(None, description="Email"),
    password1: str | None = Form(None, description="Пароль"),
    password2: str | None = Form(None, description="Подтверждение пароля"),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
    context: dict = {},
    redirect_url_for: str = "authorization_page",
):
    """Регистрация пользователя"""
    redirect_url = request.url_for(redirect_url_for)

    try:
        form = RegisterForm(
            username=username, email=email, password1=password1, password2=password2
        )
        registration_user = Registration(form, user_repository)
        await registration_user()
    except CustomException as exc:
        context = {"errors": {exc.field: exc.message}}
        return templates.TemplateResponse(request=request, name="register.html", context=context)

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/authorization", response_class=HTMLResponse)
async def authorization_method(
    request: Request,
    email: str | None = Form(None, description="Email"),
    password: str | None = Form(None, description="Пароль"),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
    context: dict = {},
    redirect_url_for: str = "index",
):
    """Вход в систему"""
    redirect_url = request.url_for(redirect_url_for)
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    try:
        form = AuthorizationForm(email=email, password=password)
        authorization_user = Authorization(form, response, user_repository)
        await authorization_user()
    except CustomException as exc:
        context = {"errors": {exc.field: exc.message}}
        return templates.TemplateResponse(
            request=request, name="authorization.html", context=context
        )

    return response


@router.post("/logout", response_class=HTMLResponse)
async def logout_method(
    request: Request,
    response_url: str = "authorization_page",
    user: User = Depends(get_current_user),  # noqa: ARG001
):
    """Выход из системы"""
    response = RedirectResponse(
        url=request.url_for(response_url), status_code=status.HTTP_303_SEE_OTHER
    )
    user_logout(response)

    return response


@router.post("/google/oauth")
async def google_oauth(
    request: Request,  # noqa: ARG001
    oauth_provider: Provider = Depends(lambda: get_oauth_provider(Providers.GOOGLE.value)),
):
    """Получение url для логина через google"""
    url: str = oauth_provider.get_oauth_url()
    return RedirectResponse(url=url)


@router.get("/google/oauth/callback")
async def google_oauth_callback(
    request: Request,
    code: str,
    oauth_provider: Provider = Depends(lambda: get_oauth_provider(Providers.GOOGLE.value)),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Вход в систему через google"""
    response = RedirectResponse(url=request.url_for("index"))
    data: UserOAuthCreateDTO = await oauth_provider.login(code)

    oauth_login = OAuthLogin(data, response, user_repository)
    await oauth_login()

    return response
