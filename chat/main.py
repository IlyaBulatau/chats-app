from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles

from auth.endpoints import router as auth_router
from auth.middlewares import AddCurrentUserToRequestMiddleware
from chats.endpoints import router as chat_router
from chats.ws.ws import router as ws_chats_router
from core.exceptions_handlers import http_not_found_handler
from infrastructure.databases import database
from settings import BASE_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    await database.init()
    yield


app = FastAPI(title="Chats App", lifespan=lifespan)


app.mount("/static", StaticFiles(directory=BASE_DIR.joinpath("static")), name="static")

app.add_middleware(AddCurrentUserToRequestMiddleware)

app.include_router(chat_router)
app.include_router(ws_chats_router)
app.include_router(auth_router)


app.add_exception_handler(status.HTTP_404_NOT_FOUND, http_not_found_handler)  # type: ignore
