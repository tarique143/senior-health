# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)

    # Use strings for class names in relationships to avoid circular imports
    medications = relationship("Medication", back_populates="owner")
    appointments = relationship("Appointment", back_populates="owner")
    contacts = relationship("Contact", back_populates="owner")