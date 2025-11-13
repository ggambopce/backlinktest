from fastapi import APIRouter
from pydantic import BaseModel
from app.stores.storage import store
from app.schemas import JobRequest

router = APIRouter(prefix="/api/backlink", tags=["Backlink"])

@router.post("/job")
async def create_job(req: JobRequest):
    job_id = await store.enqueue_job(req.keyword, req.backlinkUrl, req.number)
    return {"ok": True, "jobId": job_id}

    @router.get("/queue/status")
async def queue_status():
    # 대기열(job_queue)과 전체 job 상태 출력
    jobs = {jid: job.__dict__ for jid, job in store.jobs.items()}
    queue = list(store.job_queue)
    devices = store.devices
    return {
        "queue": queue,          # 대기 중인 job_id 리스트
        "jobs": jobs,            # 각 job 상세
        "devices": devices       # 등록된 디바이스 상태
    }