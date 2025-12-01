# app/core/security.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from app.schemas.auth import CurrentUser
from app.services.jwt_service import try_decode_access_token, InvalidTokenError

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        # Authorization 헤더 없으면 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="지원하지 않는 인증 방식입니다.",
        )

    token = credentials.credentials

    try:
        payload = try_decode_access_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )

    # 여기서는 payload 구조를 {"user_id": ..., "email": ..., "loginType": ...} 라고 가정
    user_id = payload.get("user_id")
    email = payload.get("email")
    login_type = payload.get("loginType", "normal")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 필수 정보가 없습니다.",
        )

    return CurrentUser(user_id=user_id, email=email, loginType=login_type)
