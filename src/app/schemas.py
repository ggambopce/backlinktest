from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Literal, List, Optional

DeviceState = Literal["IDLE", "RUNNING"]

class HeartbeatRequest(BaseModel):
    deviceId: str = Field(min_length=1)
    state: DeviceState
    lastJobId: Optional[str] = None  # 직전 작업 아이디(있으면 전달)

class JobEnqueueRequest(BaseModel):
    keyword: str = Field(min_length=1)
    backlinkUrl: AnyHttpUrl
    number: int = Field(ge=1, le=100)

class JobPayload(BaseModel):
    jobId: str
    keyword: str
    backlinkUrl: AnyHttpUrl
    number: int

class HeartbeatResponseNone(BaseModel):
    action: Literal["NONE"]

class HeartbeatResponseRun(BaseModel):
    action: Literal["RUN"]
    job: JobPayload

class JobResultItem(BaseModel):
    targetUrl: AnyHttpUrl
    newBacklink: AnyHttpUrl

class JobResultReport(BaseModel):
    jobId: str
    status: Literal["SUCCESS", "FAILED"]
    results: List[JobResultItem] = []
    error: Optional[str] = None

class JobRequest(BaseModel):
    keyword: str
    backlinkUrl: str
    number: int