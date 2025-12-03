# app/models/match.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from app.models.enums import MatchStatus

from datetime import datetime

from app.db import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)

    # 매칭된 두 사용자
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 매칭 상태
    status = Column(SAEnum(MatchStatus), default=MatchStatus.MATCHED, nullable=False)

    # 둘 다 채팅 승인했는지 여부
    is_chat_accepted_by_a = Column(Boolean, default=False)
    is_chat_accepted_by_b = Column(Boolean, default=False)

    # 둘 다 공개 승인했는지 여부
    is_contact_shared_by_a = Column(Boolean, default=False)
    is_contact_shared_by_b = Column(Boolean, default=False)

    # 전체 궁합 스코어 (0~100 같은 범위)
    compatibility_score = Column(Integer, nullable=True)
    # 궁합 리포트 (1~2 단락 정도 텍스트)
    compatibility_report = Column(Text, nullable=True)


    # 채팅방 연동용
    chat_room_id = Column(String(100), nullable=True)
    chat_expires_at = Column(DateTime, nullable=True)

    # match 생성 일시
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])
