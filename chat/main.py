from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from auth.endpoints import router as auth_router
from chats.endpoints import router as chat_router
from chats.ws import router as ws_chats_router
from core.database.tables import setup_mapper
from settings import BASE_DIR


app = FastAPI(title="Chats App")
app.mount("/static", StaticFiles(directory=BASE_DIR.joinpath("static")), name="static")

ROUTERS = [chat_router, ws_chats_router, auth_router]


def include_routers(app: FastAPI, routers: list[APIRouter]) -> None:
    """Регистрация роутеров"""
    for router in routers:
        app.include_router(router)


@app.on_event("startup")
async def startup():
    setup_mapper()


include_routers(app, ROUTERS)
