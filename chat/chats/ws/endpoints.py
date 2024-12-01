import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from auth.dependencies import get_current_user
from chats.ws.manager import WebsocketChatManager
from core.dependencies import get_repository
from core.domains import User
from infrastructure.repositories.chats import ChatRepository


router = APIRouter(tags=["messages"], prefix="/chats")
logger = logging.getLogger("uvicorn")


@router.websocket("/{chat_uid}")
async def ws_chats(
    websocket: WebSocket,
    chat_uid: UUID,
    current_user: User = Depends(get_current_user),
    chat_repository: ChatRepository = Depends(get_repository(ChatRepository)),
):
    logger.info("Client Connected")

    manager = WebsocketChatManager(websocket, chat_uid, current_user, chat_repository)

    await websocket.accept()

    try:
        while True:
            await manager.receive_message()
            await manager.broadcast_message()
    except WebSocketDisconnect:
        manager.disconnect()
        logger.info("Client Disconnected")
