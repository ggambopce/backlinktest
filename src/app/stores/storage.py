import asyncio                              # 비동기 동작을 지원하는 파이썬 모듈
import uuid                                 # 고유한 job ID 생성
from typing import Optional, Dict, Deque    
from collections import deque               # FIFO 큐를 위한 Deque 타입
from dataclasses import dataclass, field    # Job 구조체처럼 사용되는 간단한 데이터 모델 정의

# 하나의 작업 단위를 표현하는 데이터 구조체
@dataclass
class Job:
    job_id: str
    keyword: str                                # 백링크 키워드
    backlink_url: str                           # 백링크 URL
    number: int                                 # 게시글 성공 수
    assigned_device: Optional[str] = None       # 할당된 디바이스 ID    
    status: str = "QUEUED"                      # QUEUED / RUNNING / SUCCESS / FAILED
    results: list = field(default_factory=list) # 작업 완료후 결과 리스트

# 작업과 디바이스 상태를 메모리에 저장, 관리하는 클래스
class MemoryStore:
    def __init__(self):
        self._lock = asyncio.Lock()             # 동시성 제어를 위한 비동기 락
        self.jobs: Dict[str, Job] = {}          # job_id -> Job 객체
        self.job_queue: Deque[str] = deque()    # 작업 대기열 (job_id 순서대로)
        self.devices: Dict[str, dict] = {}      # deviceId -> {state, last_seen, running_job}

    # 새로운 작업을 큐에 등록하는 함수
    async def enqueue_job(self, device_id: str, keyword: str, backlink_url: str, number: int) -> str:
        async with self._lock:
            job_id = uuid.uuid4().hex
            job = Job(job_id, keyword, backlink_url, number)
            job.assigned_device = device_id
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
            return job_id

    # IDLE 상태인 디바이스에 작업을 할당하는 함수
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

    # 디바이스 상태를 갱신하는 함수
    async def update_device(self, device_id: str, state: str | None):
        async with self._lock:
            d = self.devices.setdefault(device_id, {})
            d["state"] = state
            d["last_seen"] = asyncio.get_event_loop().time()
        
    # 작업 완료 보고를 처리하는 함수
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
