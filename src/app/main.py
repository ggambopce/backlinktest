from fastapi import FastAPI
from .routers import machine
from .routers import userJob
from .routers import profile
from .core.database import Base, engine

app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)
app.include_router(userJob.router)
app.include_router(profile.router)

# 개발 단계에서는 자동 테이블 생성
Base.metadata.create_all(bind=engine)