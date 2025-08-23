# backend/app/routes/contact_routes.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import models
from .database import get_db
from .schemas import contact_schema
from .auth import get_current_user

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

@router.post("/", response_model=contact_schema.ContactShow, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: contact_schema.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new emergency contact for the current user."""
    existing_contacts_count = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).count()
    if existing_contacts_count >= 5: # Limit increased to 5
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add more than 5 emergency contacts."
        )

    new_contact = models.Contact(**contact.model_dump(), owner_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.get("/", response_model=List[contact_schema.ContactShow])
def get_all_user_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a list of all emergency contacts for the current user."""
    contacts = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).all()
    return contacts

@router.put("/{contact_id}", response_model=contact_schema.ContactShow)
def update_contact(
    contact_id: int,
    contact_update: contact_schema.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates a specific emergency contact by its ID."""
    contact_query = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == current_user.id
    )
    db_contact = contact_query.first()

    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
        
    update_data = contact_update.model_dump(exclude_unset=True)
    contact_query.update(update_data, synchronize_session=False)
    
    db.commit()
    updated_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    return updated_contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes an emergency contact by its ID."""
    contact_query = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == current_user.id
    )
    contact = contact_query.first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    
    contact_query.delete(synchronize_session=False)
    db.commit()
    
    return None
