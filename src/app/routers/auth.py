# app/routers/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.common import ApiResponse
from app.schemas.auth import SocialLoginRequest, CurrentUser
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.core.security import get_current_user

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/api/auth/social/login", response_model=ApiResponse)
async def social_login(
    body: SocialLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.social_login(body)
    # 여기서만 ApiResponse 포맷으로 감싸서 반환
    return ApiResponse(
        code=200,
        message="소셜로그인 성공",
        result=result.dict(),
    )

@router.get("/api/auth/me", response_model=ApiResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    # JWT에서 이미 검증이 끝난 유저 정보 사용
    result = {
        "email": current_user.email,
        "loginType": current_user.loginType,
    }
    return ApiResponse(
        code=200,
        message="로그인 사용자 정보",
        result=result,
    )