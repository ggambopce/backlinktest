from pydantic import BaseModel, AnyHttpUrl, Field, root_validator
from typing import List, Optional, Literal, Any
from urllib.parse import urlparse


DeviceState = Literal["IDLE", "RUNNING"]

class BoardModel(BaseModel): # 어디에 쓸지
    siteType: Literal["GnuBoard", "XE", "Imweb", "Cafe24", "Unknown"] = "Unknown"
    siteDomain: str          # 도메인
    siteBaseUrl: str         # 상대경로 보정
    boardName: Optional[str] = None
    boardNames: List[str] = Field(default_factory=list)
    boardUrl: Optional[str] = None

class AccountModel(BaseModel): # 로그인이 필요한 경우
    loginRequired: bool = False
    userName: str = ""
    password: str = ""
    email: str = ""

class PostModel(BaseModel): # 무엇을 쓸지
    title: str
    content: str
    useHtml: bool = True

class OptionsModel(BaseModel): # 실패,캡차,재시도 옵션
    allowCaptcha: bool = True
    retryCount: int = 3
    checkAllBoards: bool = False

class BoardWriteJobRequest(BaseModel):
    jobType: Literal["BOARD_WRITE"] = "BOARD_WRITE"

    # ✅ 최소 입력도 받기 위한 필드 추가
    keyword: Optional[str] = None
    backlinkUrl: Optional[AnyHttpUrl] = None
    targetBoardUrl: Optional[AnyHttpUrl] = None
    siteType: Optional[Literal["GnuBoard", "XE", "Imweb", "Cafe24", "Unknown"]] = None  # 선택

    # ✅ 기존 구조도 그대로 받기
    board: Optional[BoardModel] = None
    account: Optional[AccountModel] = None
    post: Optional[PostModel] = None
    options: OptionsModel = OptionsModel()

    @root_validator(pre=True)
    def _fill_minimum_fields(cls, values):
        # 이미 board/post가 오면 그대로 사용
        if values.get("board") and values.get("post"):
            return values

        keyword = values.get("keyword") or ""
        backlink = values.get("backlinkUrl")
        target_board = values.get("targetBoardUrl") or values.get("boardUrl")

        if not target_board:
            # board/post를 못 만드는 상태 -> 기존대로 검증 에러 나게 둠
            return values

        u = urlparse(str(target_board))
        site_domain = f"{u.scheme}://{u.netloc}"

        # board 자동 생성
        if not values.get("board"):
            values["board"] = {
                "siteType": values.get("siteType") or "Unknown",
                "siteDomain": site_domain,
                "siteBaseUrl": site_domain,
                "boardUrl": str(target_board),
                "boardNames": []
            }

        # post 자동 생성 (backlinkUrl이 없으면 본문에 링크를 못 넣으니 최소한 빈 링크 방지)
        if not values.get("post"):
            title = values.get("title") or f"{keyword} 정보 공유"
            content = values.get("content") or f"<p>{keyword} 관련 내용을 공유한다.</p>"
            if backlink:
                content += f"<p><a href=\"{backlink}\">{keyword}</a></p>"
            values["post"] = {
                "title": title,
                "content": content,
                "useHtml": True
            }

        return values

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