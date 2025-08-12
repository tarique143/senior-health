# backend/app/models/tip.py
from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, default="General") # e.g., Diet, Exercise, Mental Health
    content = Column(Text, nullable=False)