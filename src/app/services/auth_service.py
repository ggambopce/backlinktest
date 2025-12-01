# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.auth import SocialLoginRequest, AuthResult, UserInfo
from app.services.google_auth import verify_google_id_token
from app.services.apple_auth import verify_apple_id_token
from app.services.jwt_service import create_access_token, create_refresh_token
from app.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def social_login(self, body: SocialLoginRequest) -> AuthResult:
        # 1) provider별 토큰 검증
        if body.provider == "google":
            payload = await verify_google_id_token(body.idToken)
            social_id = payload["sub"]
            email = payload.get("email")
            login_type = "google"

        elif body.provider == "apple":
            payload = await verify_apple_id_token(body.idToken)
            social_id = payload["sub"]
            email = payload.get("email")
            login_type = "apple"

        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 provider")

        if not email:
            # 이메일 필수 정책
            raise HTTPException(status_code=400, detail="이메일 정보를 가져올 수 없음")

        # 2) 유저 조회 또는 생성
        user = (
            self.db.query(User)
            .filter(
                User.social_provider == body.provider,
                User.social_id == social_id,
            )
            .first()
        )

        if not user:
            user = User(
                email=email,
                social_provider=body.provider,
                social_id=social_id,
                login_type=login_type,
            )
            self.db.add(user)
            # PK(id) 확보를 위해 flush; commit은 맨 마지막에 한 번만
            self.db.flush()

        # 3) 우리 서비스용 JWT 생성
        #    이 시점에는 user.id가 보장된다.
        at = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "loginType": user.login_type,
            }
        )
        rt = create_refresh_token({"user_id": user.id})

        # 4) RT 저장 후 최종 커밋
        user.refresh_token = rt
        self.db.commit()
        self.db.refresh(user)

        return AuthResult(
            accessToken=at,
            refreshToken=rt,
            user=UserInfo(email=user.email, loginType=user.login_type),
        )
