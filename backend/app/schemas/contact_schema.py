# backend/app/schemas/contact_schema.py (Updated)

from pydantic import BaseModel, Field
from typing import Optional, Annotated

# Base schema with common fields
class ContactBase(BaseModel):
    name: str
    # Use Annotated for validation on the phone number
    phone_number: Annotated[str, Field(min_length=10, max_length=15)]
    relationship_type: Optional[str] = None

# Schema for creating a new contact
class ContactCreate(ContactBase):
    pass

# Schema for updating an existing contact
class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[Annotated[str, Field(min_length=10, max_length=15)]] = None
    relationship_type: Optional[str] = None

# Schema for displaying contact info
class ContactShow(ContactBase):
    id: int

    class Config:
        from_attributes = True