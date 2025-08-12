# backend/app/schemas/medication_schema.py (Sahi Code)

from pydantic import BaseModel
from datetime import time
from typing import Optional

# Base schema with common fields
class MedicationBase(BaseModel):
    name: str
    dosage: str
    timing: time
    is_active: Optional[bool] = True

# Schema for creating a medication
class MedicationCreate(MedicationBase):
    pass

# Schema for updating an existing medication
class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    timing: Optional[time] = None
    is_active: Optional[bool] = None

# Schema for displaying medication info
class MedicationShow(MedicationBase): # <-- YEH CLASS HONA ZAROORI HAI
    id: int

    class Config:
        from_attributes = True