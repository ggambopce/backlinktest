from fastapi import APIRouter, HTTPException
from ..schemas.heartbeat import (
    HeartbeatRequest, HeartbeatResponseNone, HeartbeatResponseRun,
    JobEnqueueRequest, JobResultReport, JobPayload
)
from ..stores.storage import store

router = APIRouter(prefix="/api/backlink/machine", tags=["Backlink-Machine"])

@router.post("/heartbeat", responses={
    200: {"model": HeartbeatResponseNone | HeartbeatResponseRun}
})
async def heartbeat(hb: HeartbeatRequest):
    # 디바이스 상태 갱신
    await store.update_device(hb.deviceId, hb.state)

    # IDLE이면 작업 할당 시도
    if hb.state == "IDLE":
        job = await store.assign_job_if_any(hb.deviceId)
        if job:
            return HeartbeatResponseRun(
                action="RUN",
                job=JobPayload(
                    jobId=job.jobId,
                    jobType=job.jobType,
                    payload=job.payload
                )
            )
    # 작업 없음
    return HeartbeatResponseNone(action="NONE")

@router.post("/result")
async def report_result(report: JobResultReport):
    ok = await store.complete_job(report)
    if not ok:
        raise HTTPException(status_code=404, detail="job not found")
    return {"ok": True}

