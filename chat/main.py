from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles

from auth.endpoints import router as auth_router
from auth.middlewares import AddCurrentUserToRequestMiddleware
from backgroud_tasks.broker import broker
from chats.endpoints import router as chat_router
from chats.ws.endpoints import router as ws_chats_router
from core.exceptions_handlers import http_not_found_handler, http_unauthorized_handler
from infrastructure.databases import database
from settings import BASE_DIR


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


app = FastAPI(title="Chats App", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR.joinpath("static")), name="static")

app.add_middleware(AddCurrentUserToRequestMiddleware)

app.include_router(chat_router)
app.include_router(ws_chats_router)
app.include_router(auth_router)

app.add_exception_handler(status.HTTP_404_NOT_FOUND, http_not_found_handler)
app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, http_unauthorized_handler)
