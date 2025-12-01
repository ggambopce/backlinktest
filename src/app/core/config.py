from pydantic import BaseModel
from datetime import timedelta


class JwtSettings(BaseModel):
    access_secret_key: str = "ACCESS_SECRET_KEY_CHANGE_ME"
    refresh_secret_key: str = "REFRESH_SECRET_KEY_CHANGE_ME"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 3    # 3시간
    refresh_token_expire_days: int = 30          # 30일

    @property
    def access_expires_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_expires_delta(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)


jwt_settings = JwtSettings()
