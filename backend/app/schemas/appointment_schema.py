# backend/app/schemas/appointment_schema.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Base Schema ---
class AppointmentBase(BaseModel):
    """
    Base schema containing fields common to all appointment-related operations.
    """
    doctor_name: str = Field(..., max_length=100, description="The name of the doctor or hospital.")
    appointment_datetime: datetime = Field(..., description="The date and time of the appointment.")
    purpose: Optional[str] = Field(None, max_length=255, description="The reason for the visit.")
    location: Optional[str] = Field(None, max_length=255, description="The address or location of the appointment.")


# --- Create Schema ---
class AppointmentCreate(AppointmentBase):
    """
    Schema used for creating a new appointment.
    Inherits all fields from AppointmentBase. No additional fields are needed.
    """
    pass


# --- Update Schema ---
class AppointmentUpdate(BaseModel):
    """
    Schema used for updating an existing appointment.
    All fields are optional, so the client only needs to send the data they want to change.
    """
    doctor_name: Optional[str] = Field(None, max_length=100)
    appointment_datetime: Optional[datetime] = None
    purpose: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)


# --- Display Schema ---
class AppointmentShow(AppointmentBase):
    """
    Schema used for displaying appointment information in API responses.
    This includes the appointment's database ID.
    """
    id: int

    class Config:
        # Pydantic v2 setting to allow creating the schema from an ORM model.
        # This tells Pydantic to read data from attributes, not just dict keys.
        from_attributes = True
