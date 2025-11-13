from fastapi import FastAPI
from .routers import machine
from .routers import userJob

app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)
app.include_router(userJob.router)
