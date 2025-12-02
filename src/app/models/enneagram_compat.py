# src/app/models/enneagram_compat.py
from sqlalchemy import Column, Integer, Text, String, UniqueConstraint
from app.core.database import Base


class EnneagramCompat(Base):
    __tablename__ = "enneagram_compat"

    id = Column(Integer, primary_key=True, index=True)
    male_type = Column(Integer, nullable=False)    # 1~9
    female_type = Column(Integer, nullable=False)  # 1~9
    paragraph = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("male_type", "female_type"),
    )
