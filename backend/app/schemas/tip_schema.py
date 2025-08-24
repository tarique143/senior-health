# backend/app/schemas/tip_schema.py

from typing import Optional

from pydantic import BaseModel, Field


# --- Base Schema ---
class TipBase(BaseModel):
    """

    Base schema containing fields common to all tip-related operations.
    """
    category: str = Field(
        "General",
        max_length=50,
        description="The category of the tip (e.g., 'Diet', 'Exercise')."
    )
    content: str = Field(..., description="The main text content of the health tip.")


# --- Create Schema ---
class TipCreate(TipBase):
    """
    Schema used for creating a new health tip (e.g., by an admin).
    Inherits all fields from TipBase.
    """
    pass


# --- Display Schema ---
class TipShow(TipBase):
    """
    Schema used for displaying a health tip in an API response.
    Includes the tip's unique database ID.
    """
    id: int

    class Config:
        # Pydantic v2 setting to allow creating the schema from an ORM model.
        from_attributes = True
