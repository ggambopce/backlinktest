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

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2: orm_mode 대체

    id: int
    profile_image_url: str
    temperament: str | None = None
    enneagram: str | None = None
    introduction: str | None = None
    job: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    location: str | None = None
    temperament_report: str | None = None
    sns_url: str | None = None
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime

class ProfileCreate(ProfileBase):
    pass

class ApiResponse(BaseModel):
    code: int
    message: str
    result: ProfileResponse | None = None