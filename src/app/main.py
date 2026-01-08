from fastapi import FastAPI
from .routers import machine
from .routers import userJob

from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)
app.include_router(userJob.router)


# 정적 파일 제공: /static/test_chat.html 로 접근 가능
app.mount(
    "/static",  # URL prefix
    StaticFiles(directory="src/app"),  # 실제 파일 위치 (프로젝트 루트 기준)
    name="static",
)