from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import date, datetime



class ProfileBase(BaseModel):
    profile_image_url: Optional[str] = None
    temperament: Optional[str] = None
    enneagram: Optional[str] = None
    introduction: Optional[str] = None
    job: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    temperament_report: Optional[str] = None
    sns_url: Optional[str] = None
    phone_number: Optional[str] = None


class ProfileCreate(ProfileBase):
    user_id: int

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
    temperament_report: Optional[str] = None

    helen_code: Optional[int] = None
    enneagram_maturity: Optional[int] = None
    enneagram_instinct: Optional[int] = None
    enneagram_core_type: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int
    message: str
    result: ProfileResponse | None = None