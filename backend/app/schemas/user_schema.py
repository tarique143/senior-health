# backend/app/schemas/user_schema.py

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ===================================================================
# --- Base & Create Schemas ---
# ===================================================================

class UserBase(BaseModel):
    """
    Base schema containing common user fields.
    """
    email: EmailStr = Field(..., description="The user's unique email address.")
    full_name: Optional[str] = Field(None, max_length=100, description="The user's full name.")


class UserCreate(UserBase):
    """
    Schema used for creating a new user during registration.
    Includes the password field, which is required only for creation.
    """
    password: str = Field(..., min_length=8, description="The user's password (at least 8 characters).")


# ===================================================================
# --- Update Schemas ---
# ===================================================================

class UserUpdate(BaseModel):
    """
    Schema for updating a user's profile information.
    All fields are optional to allow for partial updates.
    """
    full_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    address: Optional[str] = Field(None, max_length=255)
    # This field allows updating the user's preference for email reminders.
    send_reminders: Optional[bool] = None


class PasswordUpdate(BaseModel):
    """
    Schema for updating the user's password.
    Requires the current password for verification.
    """
    current_password: str = Field(..., description="The user's current password.")
    new_password: str = Field(..., min_length=8, description="The new password (at least 8 characters).")


# ===================================================================
# --- Password Reset Schemas ---
# ===================================================================

class ForgotPasswordRequest(BaseModel):
    """
    Schema for the 'forgot password' request.
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Schema for the 'reset password' request, containing the token and new password.
    """
    token: str = Field(..., description="The password reset token received via email.")
    new_password: str = Field(..., min_length=8)


# ===================================================================
# --- Display Schema ---
# ===================================================================

class UserShow(UserBase):
    """
    Schema for displaying public user information in API responses.
    It omits sensitive data like the hashed password.
    """
    id: int
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None
    send_reminders: bool

    class Config:
        # Pydantic v2 setting to allow creating the schema from an ORM model.
        from_attributes = True
