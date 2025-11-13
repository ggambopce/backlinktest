from pydantic import BaseModel
from typing import Optional, Any
from datetime import date

class ApiResponse(BaseModel):
    code: int
    message: str
    result: Optional[Any] = None

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
    pass
