from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Generic, TypeVar
from datetime import date, datetime


class ProfileCreate(BaseModel):

    profile_image_url: str
    introduction: Optional[str] = None
    job: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    sns_url: Optional[str] = None
    phone_number: Optional[str] = None

    # 설문 응답 (번호 그대로 받는다)
    q1: int   # 헬렌 기질 (1~4)
    q2: int   # 성숙도 (1~3)
    q3: int   # 본능 (1~3)
    q4: int   # 핵심유형 (1~9)

class ProfileResponse(BaseModel):
    id: int
    user_id: int

    profile_image_url: str
    introduction: Optional[str] = None
    job: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    sns_url: Optional[str] = None
    phone_number: Optional[str] = None

    temperament: Optional[str] = None
    enneagram: Optional[str] = None
    personal_report: Optional[str] = None

    helen_code: Optional[int] = None
    enneagram_maturity: Optional[int] = None
    enneagram_instinct: Optional[int] = None
    enneagram_core_type: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MatchOfferProfileResponse(BaseModel):
    profile_image_url: str | None = None
    introduction: str | None = None
    job: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    location: str | None = None
    temperament: str | None = None
    enneagram: str | None = None
    personal_report: str | None = None


T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    result: T | None = None