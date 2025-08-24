# backend/app/models/appointment.py

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database import Base


class Appointment(Base):
    """
    SQLAlchemy model representing a doctor's appointment.
    """
    __tablename__ = "appointments"

    # --- Table Columns ---
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    doctor_name: Mapped[str] = Column(String, index=True, nullable=False)
    purpose: Mapped[str] = Column(String, nullable=True)
    appointment_datetime: Mapped[datetime] = Column(DateTime, nullable=False)
    location: Mapped[str] = Column(String, nullable=True)

    # --- Foreign Key ---
    # This column links the appointment to a specific user.
    owner_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relationships ---
    # This creates a back-reference from the User model, allowing us to
    # easily access all appointments for a user (e.g., `user.appointments`).
    # The `back_populates` parameter must match the relationship name in the User model.
    owner: Mapped["User"] = relationship("User", back_populates="appointments")

    def __repr__(self) -> str:
        """String representation of the Appointment object."""
        return f"<Appointment(id={self.id}, doctor_name='{self.doctor_name}', owner_id={self.owner_id})>"
