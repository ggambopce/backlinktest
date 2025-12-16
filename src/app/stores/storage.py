import asyncio
import uuid
from typing import Any, Dict
from collections import deque
from dataclasses import dataclass, asdict

@dataclass
class Job:
    jobId: str
    jobType: str
    payload: Dict[str, Any]
    status: str = "QUEUED"
    assigned_device: str | None = None
    results: list[dict] | None = None
    error: str | None = None

class Store:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_queue: deque[str] = deque()
        self.devices: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def enqueue_job(self, req):
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        job = Job(
            jobId=job_id,
            jobType=req.jobType,
            payload=req.model_dump()
        )
        async with self._lock:
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
        return job_id

    async def assign_job_if_any(self, device_id: str):
        async with self._lock:
            running = self.devices.get(device_id, {}).get("running_job")
            if running:
                job = self.jobs.get(running)
                if job and job.status == "RUNNING":
                    return job

            while self.job_queue:
                jid = self.job_queue.popleft()
                job = self.jobs.get(jid)
                if not job or job.status != "QUEUED":
                    continue
                job.status = "RUNNING"
                job.assigned_device = device_id
                self.devices.setdefault(device_id, {})
                self.devices[device_id]["running_job"] = jid
                self.devices[device_id]["state"] = "BUSY"
                return job
            return None

    async def update_device(self, device_id: str, state: str | None):
        async with self._lock:
            d = self.devices.setdefault(device_id, {})
            d["state"] = state
            d["last_seen"] = asyncio.get_event_loop().time()

    async def complete_job(self, report):
        async with self._lock:
            job = self.jobs.get(report.jobId)
            if not job:
                return False
            if job.status in ("SUCCESS", "FAILED"):
                return True

            job.status = report.status
            job.results = [r.model_dump() for r in report.results]
            job.error = report.error

            if job.assigned_device:
                dev = self.devices.get(job.assigned_device, {})
                if dev.get("running_job") == job.jobId:
                    dev["running_job"] = None
                dev["state"] = "IDLE"
            return True

store = Store()
