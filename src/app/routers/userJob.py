from fastapi import APIRouter
from ..stores.storage import store
from ..schemas.heartbeat import JobEnqueueRequest
from ..schemas.common import ApiResponse

router = APIRouter(prefix="/api/backlink", tags=["Backlink"])

@router.post("/job")
async def create_job(req: JobEnqueueRequest):
    job_id = await store.enqueue_job(req)
    return ApiResponse(
        code=200,
        message="작업 큐 저장 성공",
        result={"jobId": job_id}
    )

@router.get("/queue/status")
async def queue_status():
    # queue: jobId 리스트
    queue = list(store.job_queue)

    # jobs: dict -> list (명세대로)
    jobs_list = []
    for job in store.jobs.values():
        p = job.payload
        jobs_list.append({
            "jobId": job.jobId,
            "keyword": p["keyword"],
            "backlinkUrl": p["backlinkUrl"],
            "number": p["number"],
            "assignedDevice": job.assignedDevice,
            "status": job.status,
            "results": job.results or [],
        })

    # devices: dict -> list (명세대로)
    devices_list = []
    for d in store.devices.values():
        devices_list.append({
            "deviceId": d.get("deviceId"),
            "state": d.get("state"),
            "runningJobId": d.get("runningJobId"),
        })

    return {
        "queue": queue,
        "jobs": jobs_list,
        "devices": devices_list
    }
