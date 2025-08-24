# backend/app/schemas/medication_schema.py

from datetime import time
from typing import Optional

from pydantic import BaseModel, Field


# --- Base Schema ---
class MedicationBase(BaseModel):
    """
    Base schema containing fields common to all medication-related operations.
    """
    name: str = Field(..., max_length=100, description="The name of the medication.")
    dosage: str = Field(..., max_length=50, description="The dosage instructions (e.g., '1 tablet', '10mg').")
    timing: time = Field(..., description="The time of day the medication should be taken.")
    is_active: bool = Field(True, description="Whether the medication is currently being taken.")


# --- Create Schema ---
class MedicationCreate(MedicationBase):
    """
    Schema used when creating a new medication record.
    Inherits all fields and validation from MedicationBase.
    """
    pass


# --- Update Schema ---
class MedicationUpdate(BaseModel):
    """
    Schema used when updating an existing medication.
    All fields are optional to allow for partial updates.
    """
    name: Optional[str] = Field(None, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)
    timing: Optional[time] = None
    is_active: Optional[bool] = None


# --- Display Schema ---
class MedicationShow(MedicationBase):
    """
    Schema used for displaying medication information in API responses.
    Includes the medication's unique database ID.
    """
    id: int

    class Config:
        # Pydantic v2 setting to allow creating the schema from an ORM model.
        from_attributes = True
