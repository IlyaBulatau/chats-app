from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter(prefix="/ws", tags=["chats"])
clients: list[WebSocket] = []


@router.websocket("/chats/{client_id}")
async def ws_chats(websocket: WebSocket, client_id: int):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for connect in clients:
                await connect.send_text(f"Message from client: {client_id}: {data}")
    except WebSocketDisconnect:
        clients.remove(websocket)
        for connect in clients:
            await connect.send_text(f"Client {client_id} leave chat")