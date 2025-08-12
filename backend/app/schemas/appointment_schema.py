# backend/app/schemas/appointment_schema.py (Updated)

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base schema with common fields
class AppointmentBase(BaseModel):
    doctor_name: str
    appointment_datetime: datetime
    purpose: Optional[str] = None
    location: Optional[str] = None

# Schema for creating an appointment
class AppointmentCreate(AppointmentBase):
    pass

# Schema for updating an existing appointment
class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    purpose: Optional[str] = None
    location: Optional[str] = None

# Schema for displaying appointment info
class AppointmentShow(AppointmentBase):
    id: int

    class Config:
        from_attributes = True