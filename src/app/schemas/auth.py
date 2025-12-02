# app/schemas/auth.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class SocialLoginRequest(BaseModel):
    provider: Literal["google", "apple"]
    idToken: Optional[str] = Field(None, description="Google/Apple ID Token")
    deviceId: Optional[str] = None


class UserInfo(BaseModel):
    email: str
    loginType: str


class AuthResult(BaseModel):
    accessToken: str
    refreshToken: str
    user: UserInfo

class CurrentUser(BaseModel):
    user_id: int
    email: str
    loginType: Literal["normal", "google", "apple", "kakao", "naver"] | str = "normal"