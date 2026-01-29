from fastapi import FastAPI
from .routers import machine
from .routers import userJob
from .routers import profile
from .core.database import Base, engine
from .core.scheduler import start_scheduler, shutdown_scheduler
from .routers import chat_websocket
from .routers import auth
from .routers import match
from .routers import chat
from fastapi.staticfiles import StaticFiles

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException

from .routers import dev_auth


app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)
app.include_router(userJob.router)
app.include_router(profile.router)
app.include_router(chat_websocket.router)
app.include_router(auth.router)
app.include_router(match.router)
app.include_router(chat.router)
app.include_router(dev_auth.router)

# 개발 단계에서는 자동 테이블 생성
Base.metadata.create_all(bind=engine)

# 정적 파일 제공: /static/test_chat.html 로 접근 가능
app.mount(
    "/static",  # URL prefix
    StaticFiles(directory="src/app"),  # 실제 파일 위치 (프로젝트 루트 기준)
    name="static",
)

@app.on_event("startup")
def on_startup():
    # 기타 초기화 로직들 있다면 여기서 같이 실행
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(exc.detail), "result": None},
    )