from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = []  # 연결된 모든 클라이언트를 저장

    async def connect(self, webSocket: WebSocket):
        await webSocket.accept()                        # 클라이언트 연결 수락
        self.active_connections.append(webSocket)

    def disconnect(self, webSocket: WebSocket):
        if webSocket in self.active_connections:        
            self.active_connections.remove(webSocket)   # 연결 제거
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)       # 연결된 모든 클라이언트에게 메시지 전송