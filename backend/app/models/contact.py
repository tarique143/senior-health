# backend/app/models/contact.py

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.database import Base


class Contact(Base):
    """
    SQLAlchemy model representing an emergency contact.
    """
    __tablename__ = "contacts"

    # --- Table Columns ---
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, index=True, nullable=False)
    phone_number: Mapped[str] = Column(String, nullable=False)
    relationship_type: Mapped[str] = Column(String, nullable=True)

    # --- Foreign Key ---
    # This column links the contact to a specific user.
    owner_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relationships ---
    # Creates a back-reference from the User model, so we can access
    # a user's contacts via `user.contacts`.
    owner: Mapped["User"] = relationship("User", back_populates="contacts")

    # --- Table Constraints ---
    # This constraint ensures that a single user cannot have two contacts
    # with the exact same phone number. This enforces data integrity at the
    # database level.
    __table_args__ = (
        UniqueConstraint('owner_id', 'phone_number', name='_owner_phone_uc'),
    )

    def __repr__(self) -> str:
        """String representation of the Contact object."""
        return f"<Contact(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
