# app/models/match.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)

    # 매칭된 두 사용자
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 매칭 상태
    status = Column(String(50), default="MATCHED")  
    # MATCHED → CHATTING → COMPLETED

    # 둘 다 채팅 승인했는지 여부
    is_chat_accepted_by_a = Column(Boolean, default=False)
    is_chat_accepted_by_b = Column(Boolean, default=False)

    # 둘 다 공개 승인했는지 여부
    is_accepted_by_a = Column(Boolean, default=False)
    is_accepted_by_b = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])
