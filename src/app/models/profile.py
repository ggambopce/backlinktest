# src/app/models/profile.py
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Date, Text, DateTime
)
from sqlalchemy import Column, Integer, String
from ..core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)

    profile_image_url = Column(String(255), nullable=False)  # 프로필 이미지
    temperament = Column(String(50), nullable=True)          # 4기질
    enneagram = Column(String(20), nullable=True)            # 에니어그램 9가지 유형
    introduction = Column(Text, nullable=True)               # 자기소개
    job = Column(String(100), nullable=True)                 # 직업
    birth_date = Column(Date, nullable=True)                 # 생년월일
    gender = Column(String(10), nullable=True)               # 성별
    location = Column(String(100), nullable=True)            # 활동지역
    temperament_report = Column(Text, nullable=True)         # 4기질 보고서
    sns_url = Column(String(255), nullable=True)             # SNS 주소
    phone_number = Column(String(20), nullable=True)         # 전화번호 

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )
