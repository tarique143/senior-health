# backend/app/models/tip.py (Fully Updated)

from sqlalchemy import Column, Integer, String, Text
from app.database import Base  # <-- BADLAV YAHAN KIYA GAYA HAI

class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, default="General")
    content = Column(Text, nullable=False)
