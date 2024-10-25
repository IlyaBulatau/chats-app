from fastapi import APIRouter, Depends, Form, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from auth.decorators import login_required, not_login
from auth.forms import AuthorizationForm, RegisterForm
from auth.oauth.constants import Providers
from auth.oauth.dispatch import get_oauth_provider
from auth.oauth.dto import UserOAuthData
from auth.oauth.login import OAuthLogin
from auth.oauth.providers import BaseOAuthProdiver
from auth.user import Authorization, Registration, user_logout
from core.database.connect import get_db
from core.database.repositories.user import UserRepository
from core.exceptions import CustomException
from settings import BASE_DIR


router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(BASE_DIR.joinpath("templates"))


@router.get("/register", response_class=HTMLResponse)
@not_login
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.get("/authorization", response_class=HTMLResponse)
@not_login
async def authorization_page(request: Request):
    return templates.TemplateResponse(request=request, name="authorization.html")


@router.post("/register", response_class=HTMLResponse)
@not_login
async def register_method(
    request: Request,
    username: str | None = Form(None),
    email: str | None = Form(None),
    password1: str | None = Form(None),
    password2: str | None = Form(None),
    db_session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(UserRepository),
    context: dict = {},
    redirect_url_for: str = "authorization_page",
):
    redirect_url = request.url_for(redirect_url_for)

    try:
        form = RegisterForm(username=username, email=email, password1=password1, password2=password2)
        registration_user = Registration(form, user_repo, db_session)
        await registration_user()
    except CustomException as exc:
        context = {"errors": {exc.field: exc.message}}
        return templates.TemplateResponse(request=request, name="register.html", context=context)

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/authorization", response_class=HTMLResponse)
@not_login
async def authorization_method(
    request: Request,
    email: str | None = Form(None),
    password: str | None = Form(None),
    db_session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(UserRepository),
    context: dict = {},
    redirect_url_for: str = "index",
):
    redirect_url = request.url_for(redirect_url_for)
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    try:
        form = AuthorizationForm(email=email, password=password)
        authorization_user = Authorization(form, response, user_repo, db_session)
        await authorization_user()
    except CustomException as exc:
        context = {"errors": {exc.field: exc.message}}
        return templates.TemplateResponse(request=request, name="authorization.html", context=context)

    return response


@router.post("/logout", response_class=HTMLResponse)
@login_required
async def logout_method(request: Request, response_url: str = "authorization_page"):
    response = RedirectResponse(url=request.url_for(response_url))
    user_logout(response)
    return response


@router.post("/google/oauth")
@not_login
async def google_oauth(
    request: Request,  # noqa: ARG001
    oauth_provider: BaseOAuthProdiver = Depends(get_oauth_provider(Providers.GOOGLE.value)),
):
    url: str = oauth_provider.get_oauth_url()
    return RedirectResponse(url=url)


@router.get("/google/oauth/callback")
async def google_oauth_callback(
    request: Request,
    code: str,
    db_session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(UserRepository),
    oauth_provider: BaseOAuthProdiver = Depends(get_oauth_provider(Providers.GOOGLE.value)),
):
    response = RedirectResponse(url=request.url_for("index"))
    data: UserOAuthData = await oauth_provider.login(code)

    oauth_login = OAuthLogin(data, response, user_repo, db_session)
    await oauth_login()

    return response
