from fastapi import FastAPI
from app.routers import machine

app = FastAPI(title="Backlink Heartbeat API", version="0.1.0")
app.include_router(machine.router)

@app.get("/")
def root():
    return {"ok": True}
