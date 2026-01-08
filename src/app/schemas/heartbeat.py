from pydantic import BaseModel, AnyHttpUrl, Field
from typing import List, Optional, Literal

DeviceState = Literal["IDLE", "RUNNING"]

class HeartbeatRequest(BaseModel):
    deviceId: str = Field(min_length=1)
    state: DeviceState
    currentJobId: Optional[str] = None

class JobPayload(BaseModel):
    jobId: str
    keyword: str
    backlinkUrl: AnyHttpUrl
    number: int = Field(ge=1, le=100)

class HeartbeatResponseRun(BaseModel):
    action: Literal["RUN"] = "RUN"
    job: JobPayload

class HeartbeatResponseNone(BaseModel):
    action: Literal["NONE"] = "NONE"
    job: None = None

class JobEnqueueRequest(BaseModel):
    keyword: str = Field(min_length=1)
    backlinkUrl: AnyHttpUrl
    number: int = Field(ge=1, le=100)

class JobResultItem(BaseModel):
    newBacklink: AnyHttpUrl

class JobResultReport(BaseModel):
    jobId: str
    status: Literal["SUCCESS", "FAILED"]
    results: List[JobResultItem] = []
    error: Optional[str] = None
