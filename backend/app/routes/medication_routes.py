# backend/app/routes/medication_routes.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Local imports
from app import models
from app.database import get_db
from app.schemas import medication_schema
from app.auth import get_current_user

router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)

@router.post("/", response_model=medication_schema.MedicationShow, status_code=status.HTTP_201_CREATED)
def create_medication(
    med: medication_schema.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new medication record for the current user."""
    new_med = models.Medication(**med.model_dump(), owner_id=current_user.id)
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/", response_model=List[medication_schema.MedicationShow])
def get_user_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a list of all medications for the current user."""
    meds = db.query(models.Medication).filter(models.Medication.owner_id == current_user.id).all()
    return meds

@router.put("/{med_id}", response_model=medication_schema.MedicationShow)
def update_medication(
    med_id: int,
    med_update: medication_schema.MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates a specific medication by its ID."""
    med_query = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    )
    
    db_med = med_query.first()

    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication with id {med_id} not found"
        )
    
    update_data = med_update.model_dump(exclude_unset=True)
    med_query.update(update_data, synchronize_session=False)
    
    db.commit()
    # After commit, the db_med object is expired, so we need to get it again.
    updated_med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    return updated_med

@router.delete("/{med_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a medication by its ID."""
    medication_query = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.owner_id == current_user.id
    )
    
    medication = medication_query.first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication with id {med_id} not found"
        )
    
    medication_query.delete(synchronize_session=False)
    db.commit()
    
    return None
