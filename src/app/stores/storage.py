import asyncio
import uuid
from typing import Any, Dict, Optional, List
from collections import deque
from dataclasses import dataclass

@dataclass
class Job:
    jobId: str
    payload: Dict[str, Any]
    status: str = "QUEUED"
    assignedDevice: Optional[str] = None   # 명세서대로 camelCase로 아예 통일(간단 버전)
    results: List[dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []


class Store:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_queue: deque[str] = deque()
        self.devices: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def enqueue_job(self, req):
        job_id = uuid.uuid4().hex
        job = Job(
            jobId=job_id,
            payload={
                "keyword": req.keyword,
                "backlinkUrl": str(req.backlinkUrl),
                "number": req.number,
            },
            status="QUEUED",
            assignedDevice=None,   # 이제 Job에 필드가 있으니 OK
            results=[],
        )
        async with self._lock:
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
        return job_id

    async def assign_job_if_any(self, device_id: str):
        async with self._lock:
            d = self.devices.setdefault(device_id, {
                "deviceId": device_id,
                "state": "IDLE",
                "runningJobId": None,
                "lastSeen": None,
            })

            # 이미 RUNNING이면 재발급 금지
            running_id = d.get("runningJobId")
            if running_id:
                job = self.jobs.get(running_id)
                if job and job.status == "RUNNING":
                    return job

            while self.job_queue:
                jid = self.job_queue.popleft()
                job = self.jobs.get(jid)
                if not job or job.status != "QUEUED":
                    continue

                job.status = "RUNNING"
                job.assignedDevice = device_id

                d["state"] = "RUNNING"
                d["runningJobId"] = jid
                d["lastSeen"] = asyncio.get_event_loop().time()

                return job

            return None

    async def update_device(self, device_id: str, state: Optional[str]):
        async with self._lock:
            d = self.devices.setdefault(device_id, {
                "deviceId": device_id,
                "state": "IDLE",
                "runningJobId": None,
                "lastSeen": None,
            })
            if state:
                d["state"] = state
            d["lastSeen"] = asyncio.get_event_loop().time()

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

            if job.assignedDevice:
                d = self.devices.get(job.assignedDevice)
                if d and d.get("runningJobId") == job.jobId:
                    d["runningJobId"] = None
                    d["state"] = "IDLE"
                    d["lastSeen"] = asyncio.get_event_loop().time()

            return True


store = Store()
