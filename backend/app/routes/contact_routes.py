# backend/app/routes/contact_routes.py (Updated with Error Handling)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models
from app.database import get_db
from app.schemas import contact_schema
from app.auth import get_current_user

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
    # Check 1: Limit the total number of contacts
    existing_contacts_count = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).count()
    if existing_contacts_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add more than 5 emergency contacts."
        )

    ### --- NAYA BADLAV YAHAN HUA HAI (START) --- ###
    # Check 2: Prevent duplicate phone numbers for the SAME user
    existing_contact_with_phone = db.query(models.Contact).filter(
        models.Contact.phone_number == contact.phone_number,
        models.Contact.owner_id == current_user.id
    ).first()

    if existing_contact_with_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict is a better status code for this
            detail=f"A contact with the phone number '{contact.phone_number}' already exists."
        )
    ### --- NAYA BADLAV YAHAN HUA HAI (END) --- ###

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
    
    ### --- NAYA BADLAV (UPDATE KE LIYE) --- ###
    # Also check for duplicate phone numbers when updating
    if contact_update.phone_number and contact_update.phone_number != db_contact.phone_number:
        existing_contact_with_phone = db.query(models.Contact).filter(
            models.Contact.phone_number == contact_update.phone_number,
            models.Contact.owner_id == current_user.id
        ).first()
        if existing_contact_with_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another contact already has the phone number '{contact_update.phone_number}'."
            )
    ### --- NAYA BADLAV (END) --- ###
        
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
