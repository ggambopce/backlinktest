from fastapi import APIRouter
from pydantic import BaseModel
from ..stores.storage import store
from ..schemas.heartbeat import BoardWriteJobRequest
from dataclasses import asdict

router = APIRouter(prefix="/api/backlink", tags=["Backlink"])

@router.post("/job")
async def create_job(req: BoardWriteJobRequest):
    job_id = await store.enqueue_job(req)   # 전체 req 저장
    return {"ok": True, "jobId": job_id}

@router.get("/queue/status")
async def queue_status():
    jobs = {jid: asdict(job) for jid, job in store.jobs.items()}
    queue = list(store.job_queue)
    devices = store.devices
    return {"queue": queue, "jobs": jobs, "devices": devices}