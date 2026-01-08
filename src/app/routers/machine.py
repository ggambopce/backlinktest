from fastapi import APIRouter, HTTPException
from ..schemas.heartbeat import (
    HeartbeatRequest, HeartbeatResponseNone, HeartbeatResponseRun,
    JobResultReport, JobPayload
)
from ..stores.storage import store

router = APIRouter(prefix="/api/backlink/machine", tags=["Backlink-Machine"])

@router.post("/heartbeat", responses={200: {"model": HeartbeatResponseNone | HeartbeatResponseRun}})
async def heartbeat(hb: HeartbeatRequest):
    await store.update_device(hb.deviceId, hb.state)

    if hb.state == "IDLE":
        job = await store.assign_job_if_any(hb.deviceId)
        if job:
            p = job.payload
            return HeartbeatResponseRun(
                action="RUN",
                job=JobPayload(
                    jobId=job.jobId,
                    keyword=p["keyword"],
                    backlinkUrl=p["backlinkUrl"],
                    number=p["number"],
                )
            )

    return HeartbeatResponseNone(action="NONE", job=None)

@router.post("/result")
async def report_result(report: JobResultReport):
    ok = await store.complete_job(report)
    if not ok:
        raise HTTPException(status_code=404, detail="job not found")
    return {"ok": True}
