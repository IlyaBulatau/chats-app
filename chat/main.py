from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from application.auth.middlewares import AddCurrentUserToRequestMiddleware
from application.backgroud_tasks.broker import broker
from infrastructure.databases import database
from presentation.html.auth import router as auth_html_router
from presentation.html.chats import router as chats_html_router
from presentation.html.exception_handlers import http_not_found_handler, http_unauthorized_handler
from presentation.rest.auth import router as auth_rest_router
from presentation.rest.exception_handlers import http_unauthorized_api_handler
from presentation.rest.exceptions import APIUnauthorizedError
from presentation.ws.chats import router as chats_ws_router
from settings import APP_SETTINGS, BASE_DIR


logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    await database.init()

    if not broker.is_worker_process:
        await broker.startup()

    logger.info("App started")

    yield

    if broker.is_worker_process:
        await broker.shutdown()

    if database.is_init():
        await database.close_connection()

    logger.info("App stopped")


app = FastAPI(
    title="Chats App",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    description=(
        "**Авторизация**:\n\n"
        "При входе в систему в куки устанавливается `sessionid`,"
        "который затем проверяется на валидность при каждом запросе, "
        "и откуда достается информация о текущем пользователе.\n\n\n"
        "**Вебсокеты**:\n\n"
        "Для соединения в чате используется вебсокет по следующему ендпоинту: `/chats/{chat.uid}`. "
        "Вебсокет позволяет пользователям обмениваться сообщениями в реальном времени.\n\n\n"
        "**Текущая функциональность**:\n\n"
        "- Пользовательская авторизация через установку куки.\n"
        "- Пользовательская авторизация через гугл(по факту после "
        "получения логина тоже устанавливается куки).\n"
        "- Чат в реальном времени через вебсокеты.\n"
        "- Возможность удалять сообщения в чате.\n"
        "- Возможность слать файлы сообщением в чате.\n"
        "- Квота на размер отправленных файлов пользователем.\n"
    ),
)

app.mount("/static", StaticFiles(directory=BASE_DIR.joinpath("static")), name="static")

app.add_middleware(AddCurrentUserToRequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=APP_SETTINGS.cors_allow_origins,
)

# html routers
app.include_router(chats_html_router)
app.include_router(chats_ws_router)
app.include_router(auth_html_router)

# rest routers
app.include_router(auth_rest_router)

app.add_exception_handler(status.HTTP_404_NOT_FOUND, http_not_found_handler)
app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, http_unauthorized_handler)
app.add_exception_handler(APIUnauthorizedError, http_unauthorized_api_handler)
