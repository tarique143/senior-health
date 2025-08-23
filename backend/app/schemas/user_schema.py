# backend/app/schemas/user_schema.py (Updated)

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# --- Base and Create Schemas (No Changes) ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

# --- Update Schemas (BADLAV YAHAN HUA HAI) ---
class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    
    ### --- NAYA BADLAV: REMINDERS KE LIYE --- ###
    # Isse hum frontend se reminder setting ko update kar payenge.
    send_reminders: Optional[bool] = None

class PasswordUpdate(BaseModel):
    """Schema for updating the user's password."""
    current_password: str
    new_password: str

# --- Password Reset Schemas (No Changes) ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- Display Schema (BADLAV YAHAN HUA HAI) ---
class UserShow(UserBase):
    """Schema for displaying public user information."""
    id: int
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    ### --- NAYA BADLAV: REMINDERS KE LIYE --- ###
    # Taaki frontend par user ki current setting dikh sake.
    send_reminders: bool

    class Config:
        from_attributes = True
