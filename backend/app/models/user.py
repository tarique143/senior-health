# backend/app/models/user.py

from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database import Base


class User(Base):
    """
    SQLAlchemy model representing a user of the application.
    """
    __tablename__ = "users"

    # --- Table Columns ---
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = Column(String, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    date_of_birth: Mapped[Optional[date]] = Column(Date, nullable=True)
    address: Mapped[Optional[str]] = Column(String, nullable=True)

    # The URL path to the user's uploaded profile picture.
    # e.g., "/profile_pics/some_unique_filename.png"
    profile_picture_url: Mapped[Optional[str]] = Column(String, nullable=True)

    # User preference for receiving daily email reminders.
    send_reminders: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    # These relationships link the user to their associated data in other tables.
    # The `cascade="all, delete-orphan"` option means that if a user is deleted,
    # all of their associated medications, appointments, and contacts will be
    # automatically deleted from the database as well.

    medications: Mapped[List["Medication"]] = relationship(
        "Medication", back_populates="owner", cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="owner", cascade="all, delete-orphan"
    )
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the User object."""
        return f"<User(id={self.id}, email='{self.email}')>"
