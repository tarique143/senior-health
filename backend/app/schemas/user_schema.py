# backend/app/schemas/user_schema.py (Updated)

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# --- Base and Create Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

# --- Update Schemas ---
class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None

class PasswordUpdate(BaseModel):
    """Schema for updating the user's password."""
    current_password: str
    new_password: str

# --- Display Schema ---
class UserShow(UserBase):
    """Schema for displaying public user information."""
    id: int
    date_of_birth: Optional[date] = None
    address: Optional[str] = None

    class Config:
        # Pydantic v2 uses 'from_attributes' instead of 'orm_mode'
        from_attributes = True