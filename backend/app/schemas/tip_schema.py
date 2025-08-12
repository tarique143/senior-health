# backend/app/schemas/tip_schema.py
from pydantic import BaseModel
from typing import Optional

# Base schema with common attributes
class TipBase(BaseModel):
    content: str
    category: Optional[str] = "General"

# Schema for creating a new tip (e.g., for an admin)
class TipCreate(TipBase):
    pass

# Schema for displaying a tip to the user
class TipShow(TipBase):
    id: int

    class Config:
        # For Pydantic v2
        from_attributes = True