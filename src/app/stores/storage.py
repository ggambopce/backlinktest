import asyncio
import uuid
from typing import Optional, Dict, Deque
from collections import deque
from dataclasses import dataclass, field

@dataclass
class Job:
    job_id: str
    keyword: str
    backlink_url: str
    number: int
    assigned_device: Optional[str] = None
    status: str = "QUEUED"  # QUEUED / RUNNING / SUCCESS / FAILED
    results: list = field(default_factory=list)
    error: Optional[str] = None

class MemoryStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.jobs: Dict[str, Job] = {}
        self.job_queue: Deque[str] = deque()
        self.devices: Dict[str, dict] = {}  # deviceId -> {state, last_seen, running_job}

    async def enqueue_job(self, keyword: str, backlink_url: str, number: int) -> str:
        async with self._lock:
            job_id = uuid.uuid4().hex
            job = Job(job_id, keyword, backlink_url, number)
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
            return job_id

    async def assign_job_if_any(self, device_id: str):
        async with self._lock:
            # 이미 달려있는 작업이 있으면 그대로 유지
            running = self.devices.get(device_id, {}).get("running_job")
            if running:
                job = self.jobs.get(running)
                if job and job.status == "RUNNING":
                    return job

            # 새 작업 할당
            while self.job_queue:
                jid = self.job_queue.popleft()
                job = self.jobs.get(jid)
                if not job or job.status != "QUEUED":
                    continue
                job.status = "RUNNING"
                job.assigned_device = device_id
                # 디바이스 상태 업데이트
                self.devices.setdefault(device_id, {})
                self.devices[device_id]["running_job"] = jid
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
            # 멱등 처리: 이미 끝난 작업이면 OK
            if job.status in ("SUCCESS", "FAILED"):
                return True
            job.status = report.status
            job.results = [r.model_dump() for r in report.results]
            job.error = report.error
            # 디바이스의 running_job 비우기
            if job.assigned_device:
                dev = self.devices.get(job.assigned_device, {})
                if dev.get("running_job") == job.job_id:
                    dev["running_job"] = None
                dev["state"] = "IDLE"
            return True

store = MemoryStore()
