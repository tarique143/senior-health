# backend/app/models/medication.py

from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, relationship

from app.database import Base


class Medication(Base):
    """
    SQLAlchemy model representing a medication schedule.
    """
    __tablename__ = "medications"

    # --- Table Columns ---
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, index=True, nullable=False)
    dosage: Mapped[str] = Column(String, nullable=False)
    timing: Mapped[time] = Column(Time, nullable=False)
    # This flag allows users to temporarily disable a medication without deleting it.
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    # --- Foreign Key ---
    # Links the medication record to the user who owns it.
    owner_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relationships ---
    # Creates a back-reference from the User model, allowing access to
    # a user's medications via `user.medications`.
    owner: Mapped["User"] = relationship("User", back_populates="medications")

    def __repr__(self) -> str:
        """String representation of the Medication object."""
        return f"<Medication(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
