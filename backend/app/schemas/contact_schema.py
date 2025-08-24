# backend/app/schemas/contact_schema.py

from typing import Optional

from pydantic import BaseModel, Field


# --- Base Schema ---
class ContactBase(BaseModel):
    """
    Base schema containing fields common to all contact-related operations.
    """
    name: str = Field(..., max_length=100, description="The full name of the contact.")
    # The `pattern` argument provides regex validation for a simple phone number format.
    # It allows digits, spaces, hyphens, and parentheses, and requires at least 7 digits.
    phone_number: str = Field(
        ...,
        min_length=7,
        max_length=20,
        pattern=r"^[0-9\s\-\(\)]*$",
        description="The contact's phone number."
    )
    relationship_type: Optional[str] = Field(
        None,
        max_length=50,
        description="The contact's relationship to the user (e.g., Son, Doctor)."
    )


# --- Create Schema ---
class ContactCreate(ContactBase):
    """
    Schema used for creating a new emergency contact.
    Inherits all fields and validation from ContactBase.
    """
    pass


# --- Update Schema ---
class ContactUpdate(BaseModel):
    """
    Schema used for updating an existing contact.
    All fields are optional, allowing for partial updates.
    """
    name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(
        None,
        min_length=7,
        max_length=20,
        pattern=r"^[0-9\s\-\(\)]*$"
    )
    relationship_type: Optional[str] = Field(None, max_length=50)


# --- Display Schema ---
class ContactShow(ContactBase):
    """
    Schema used for displaying contact information in API responses.
    Includes the contact's database ID.
    """
    id: int

    class Config:
        # Pydantic v2 setting to allow creating the schema from an ORM model.
        from_attributes = True
