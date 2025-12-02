# src/app/models/temperament_compat.py
from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from app.core.database import Base


class TemperamentCompat(Base):
    __tablename__ = "temperament_compat"

    id = Column(Integer, primary_key=True, index=True)
    male_type = Column(Integer, nullable=False)   # 1~4
    female_type = Column(Integer, nullable=False) # 1~4
    paragraph = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("male_type", "female_type"),
    )
