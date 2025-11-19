from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..core.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    # 클라이언트 연결 수락 및 목록 추가
    await manager.connect(websocket)
    try:
        # 메세지 수신 무한 루프
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_json()
            sender = data.get("sender", "Anonymous")
            content = data.get("content", "")

            # 수신한 메시지를 모든 클라이언트에게 브로드캐스트
            await manager.broadcast({
                "sender": sender,
                "content": content,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)  # 연결 종료 시 목록에서 제거 