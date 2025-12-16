from pydantic import BaseModel, AnyHttpUrl, Field
from typing import List, Optional, Literal, Any

DeviceState = Literal["IDLE", "RUNNING"]

class BoardModel(BaseModel):
    siteType: Literal["GnuBoard", "XE", "Imweb", "Cafe24", "Unknown"] = "Unknown"
    siteDomain: str
    siteBaseUrl: str
    boardName: Optional[str] = None
    boardNames: List[str] = Field(default_factory=list)
    boardUrl: Optional[str] = None

class AccountModel(BaseModel):
    loginRequired: bool = False
    userName: str = ""
    password: str = ""
    email: str = ""

class PostModel(BaseModel):
    title: str
    content: str
    useHtml: bool = True

class OptionsModel(BaseModel):
    allowCaptcha: bool = True
    retryCount: int = 3

class BoardWriteJobRequest(BaseModel):
    jobType: Literal["BOARD_WRITE"] = "BOARD_WRITE"
    board: BoardModel
    account: AccountModel
    post: PostModel
    options: OptionsModel = OptionsModel()

class JobPayload(BaseModel):
    jobId: str
    jobType: Literal["BOARD_WRITE"]
    payload: Any

class HeartbeatResponseRun(BaseModel):
    action: Literal["RUN"] = "RUN"
    job: JobPayload

class HeartbeatResponseNone(BaseModel):
    action: Literal["NONE"] = "NONE"

class HeartbeatRequest(BaseModel):
    deviceId: str = Field(min_length=1)
    state: DeviceState
    lastJobId: Optional[str] = None  # 직전 작업 아이디(있으면 전달)

class JobEnqueueRequest(BaseModel):
    keyword: str = Field(min_length=1)
    backlinkUrl: AnyHttpUrl
    number: int = Field(ge=1, le=100)


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