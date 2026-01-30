# src/app/models/profile.py
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Date, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from ..core.database import Base
from .enums import HelenFisherType, EnneagramCoreType

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)

    # FK (User 1:1)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # 프로필 필드들
    profile_image_url = Column(String(255), nullable=True)  # 프로필 이미지(직접작성)
    temperament = Column(String(50), nullable=True)          # 4기질(질문지 1번)
    enneagram = Column(String(20), nullable=True)            # 에니어그램 9가지 유형(질문지 4번)
    introduction = Column(Text, nullable=True)               # 자기소개(직접작성)
    job = Column(String(100), nullable=True)                 # 직업(직접작성)
    birth_date = Column(Date, nullable=True)                 # 생년월일(직접작성)
    gender = Column(String(10), nullable=True)               # 성별(직접작성)
    location = Column(String(100), nullable=True)            # 활동지역(직접작성)
    personal_report = Column(Text, nullable=True)            # 개인 성향 보고서
    sns_url = Column(String(255), nullable=True)             # SNS 주소(직접작성)
    phone_number = Column(String(20), nullable=True)         # 전화번호(직접작성)
    # 설문 코드값들
    # ❶ 헬렌 피셔 기질 (질문지 1번: 1~4)
    helen_code = Column(Integer, nullable=True)              # 1~4
    # ❷ 에니어그램 성숙도 (질문지 2번: 1~3)
    enneagram_maturity = Column(Integer, nullable=True)      # 1=고성숙, 2=중성숙, 3=저성숙
    # ❸ 에니어그램 본능 (질문지 3번: 1~3)
    enneagram_instinct = Column(Integer, nullable=True)      # 1=자기보존, 2=사회적, 3=일대일
    # ❹ 에니어그램 핵심유형 (질문지 4번: 1~9)
    enneagram_core_type = Column(Integer, nullable=True)     # 1~9

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

    # 관계
    user = relationship("User", back_populates="profile")

# 편의용 프로퍼티 (원할 때만)
    @property
    def helen_enum(self) -> HelenFisherType | None:
        return HelenFisherType(self.helen_code) if self.helen_code else None

    @property
    def enneagram_core_enum(self) -> EnneagramCoreType | None:
        return (
            EnneagramCoreType(self.enneagram_core_type)
            if self.enneagram_core_type
            else None
        )