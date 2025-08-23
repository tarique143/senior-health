# backend/app/routes/appointment_routes.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models
from app.database import get_db
from app.schemas import appointment_schema
from app.auth import get_current_user

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=appointment_schema.AppointmentShow, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment: appointment_schema.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new appointment for the current user."""
    new_appointment = models.Appointment(
        **appointment.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/", response_model=List[appointment_schema.AppointmentShow])
def get_all_user_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a list of all appointments for the current user."""
    appointments = db.query(models.Appointment).filter(models.Appointment.owner_id == current_user.id).all()
    return appointments

@router.get("/{appointment_id}", response_model=appointment_schema.AppointmentShow)
def get_appointment_by_id(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Gets a specific appointment by its ID."""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    return appointment

@router.put("/{appointment_id}", response_model=appointment_schema.AppointmentShow)
def update_appointment(
    appointment_id: int,
    appointment_update: appointment_schema.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates a specific appointment by its ID."""
    appointment_query = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    )
    db_appointment = appointment_query.first()

    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    
    update_data = appointment_update.model_dump(exclude_unset=True)
    appointment_query.update(update_data, synchronize_session=False)
    
    db.commit()
    updated_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    return updated_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes an appointment by its ID."""
    appointment_query = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.owner_id == current_user.id
    )
    appointment = appointment_query.first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found"
        )
    
    appointment_query.delete(synchronize_session=False)
    db.commit()
    
    return None
