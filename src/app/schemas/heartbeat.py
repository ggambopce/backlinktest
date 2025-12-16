from pydantic import BaseModel, Field
from typing import List, Optional, Literal

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
