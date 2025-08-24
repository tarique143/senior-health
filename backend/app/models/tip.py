# backend/app/models/tip.py

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped

from app.database import Base


class Tip(Base):
    """
    SQLAlchemy model representing a health tip.

    These tips can be displayed to users, for example, on their dashboard.
    """
    __tablename__ = "tips"

    # --- Table Columns ---
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    # The category of the tip (e.g., "Diet", "Exercise", "Mental Health").
    category: Mapped[str] = Column(String, index=True, default="General", nullable=False)
    # The main content/text of the health tip.
    content: Mapped[str] = Column(Text, nullable=False)

    def __repr__(self) -> str:
        """String representation of the Tip object."""
        return f"<Tip(id={self.id}, category='{self.category}')>"
