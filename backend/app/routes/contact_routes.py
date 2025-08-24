# backend/app/routes/contact_routes.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db
from app.schemas import contact_schema

# Create a new router for contact-related endpoints.
router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

# Define a constant for the maximum number of contacts allowed per user.
MAX_CONTACTS_PER_USER = 5


@router.post("/", response_model=contact_schema.ContactShow, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: contact_schema.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Creates a new emergency contact for the currently authenticated user.

    Enforces two business rules:
    1. A user cannot have more than MAX_CONTACTS_PER_USER contacts.
    2. A user cannot have two contacts with the same phone number.
    """
    # Rule 1: Limit the total number of contacts per user.
    existing_contacts_count = db.query(models.Contact).filter(
        models.Contact.owner_id == current_user.id
    ).count()
    if existing_contacts_count >= MAX_CONTACTS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add more than {MAX_CONTACTS_PER_USER} emergency contacts."
        )

    # Create the new contact object.
    new_contact = models.Contact(**contact.model_dump(), owner_id=current_user.id)
    db.add(new_contact)

    try:
        db.commit()
        db.refresh(new_contact)
    except IntegrityError:
        # Rule 2: This error is raised by the unique constraint on (owner_id, phone_number) in the model.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A contact with the phone number '{contact.phone_number}' already exists."
        )
    return new_contact


@router.get("/", response_model=List[contact_schema.ContactShow])
def get_all_user_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieves a list of all emergency contacts for the currently authenticated user.
    """
    contacts = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).all()
    return contacts


@router.put("/{contact_id}", response_model=contact_schema.ContactShow)
def update_contact(
    contact_id: int,
    contact_update: contact_schema.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Updates a specific emergency contact by its ID.
    Ensures the contact belongs to the currently authenticated user.
    """
    contact_query = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == current_user.id
    )
    db_contact = contact_query.first()

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found."
        )

    update_data = contact_update.model_dump(exclude_unset=True)
    contact_query.update(update_data, synchronize_session=False)

    try:
        db.commit()
        db.refresh(db_contact)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another contact already has the phone number '{contact_update.phone_number}'."
        )
    return db_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deletes an emergency contact by its ID.
    Ensures the contact belongs to the currently authenticated user.
    """
    contact_query = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == current_user.id
    )
    contact = contact_query.first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found."
        )

    contact_query.delete(synchronize_session=False)
    db.commit()

    return None
