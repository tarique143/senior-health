# backend/app/schemas/user_schema.py (Updated with All Features)

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# --- Base and Create Schemas (No Changes) ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

# --- Update Schemas (No Changes) ---
class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None

class PasswordUpdate(BaseModel):
    """Schema for updating the user's password."""
    current_password: str
    new_password: str

### --- NAYE SCHEMAS (PASSWORD RESET KE LIYE) --- ###

class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a password reset."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Schema for resetting the password with a token."""
    token: str
    new_password: str

# --- Display Schema (Updated) ---
class UserShow(UserBase):
    """Schema for displaying public user information."""
    id: int
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    
    ### --- BADLAV YAHAN HUA HAI (PROFILE PHOTO URL KE LIYE) --- ###
    profile_picture_url: Optional[str] = None

    class Config:
        # Pydantic v2 uses 'from_attributes' instead of 'orm_mode'
        from_attributes = True
