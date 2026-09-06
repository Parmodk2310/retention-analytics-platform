from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.manager import manager

router = APIRouter(prefix="/ws", tags=["realtime"])


@router.websocket("/experiments")
async def experiments_socket(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
