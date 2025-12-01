# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 로그인 정보
    email = Column(String(255), unique=True, index=True, nullable=False)
    social_provider = Column(String(50), nullable=True)   # "google", "apple", etc
    social_id = Column(String(255), nullable=True)        # provider가 주는 sub 값
    login_type = Column(String(50), default="normal")     # normal / google / apple

    # 토큰
    refresh_token = Column(String(500), nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    profile = relationship("Profile", back_populates="user", uselist=False)
