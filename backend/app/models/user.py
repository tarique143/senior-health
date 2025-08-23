# backend/app/models/user.py (Updated)

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    
    # === YEH NAYI LINE ADD KAREIN ===
    profile_picture_url = Column(String, nullable=True)

    # Relationships
    medications = relationship("Medication", back_populates="owner", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="owner", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
