from fastapi import FastAPI
from .routers import machine
from .routers import userJob
from .routers import profile
from .core.database import Base, engine
from .routers import chat_websocket
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)
app.include_router(userJob.router)
app.include_router(profile.router)
app.include_router(chat_websocket.router)

# 개발 단계에서는 자동 테이블 생성
Base.metadata.create_all(bind=engine)

# 정적 파일 제공: /static/test_chat.html 로 접근 가능
app.mount(
    "/static",  # URL prefix
    StaticFiles(directory="src/app"),  # 실제 파일 위치 (프로젝트 루트 기준)
    name="static",
)