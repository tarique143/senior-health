# backend/app/models/medication.py
from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Medication(Base):
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dosage = Column(String)
    timing = Column(Time)
    is_active = Column(Boolean, default=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Use a string "User" here to prevent circular import errors
    owner = relationship("User", back_populates="medications")