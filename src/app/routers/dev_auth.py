# app/routers/dev_auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.jwt_service import create_access_token  # 너가 쓰는 util
from app.models.user import User

class DevLoginRequest(BaseModel):
    email: str

class DevLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter(prefix="/api/dev-auth", tags=["dev-auth"])

@router.post("/login", response_model=DevLoginResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    # 1) 해당 이메일 유저 조회 (없으면 만들기도 가능)
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # 간단히 자동 생성
        user = User(email=payload.email, login_type="normal")
        db.add(user)
        db.commit()
        db.refresh(user)

    claims = {
        "user_id": user.id,          
        "email": user.email,
        "loginType": user.login_type,
    }    

    # 2) 우리 서비스 JWT 발급
    access_token = create_access_token(claims)

    return DevLoginResponse(access_token=access_token)
