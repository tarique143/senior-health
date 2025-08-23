# backend/app/models/contact.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    relationship_type = Column(String, nullable=True)  # e.g., "Son", "Doctor", "Neighbor"
    
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Use a string "User" here to prevent circular import errors
    owner = relationship("User", back_populates="contacts")
