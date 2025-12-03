from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRoomResponse(BaseModel):
    hasActiveChat: bool
    chatRoomId: Optional[str]
    matchId: Optional[int]
    partnerNickname: Optional[str]
    chatExpiresAt: Optional[datetime]


class ChatAcceptRequest(BaseModel):
    matchId: int
    accept: bool
