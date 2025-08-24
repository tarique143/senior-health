# backend/app/routes/tip_routes.py

import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db
from app.schemas import tip_schema

# Create a new router for health tip endpoints.
router = APIRouter(
    prefix="/tips",
    tags=["Health Tips"]
)


@router.get("/random", response_model=tip_schema.TipShow)
def get_random_tip(db: Session = Depends(get_db)):
    """
    Fetches a single random health tip from the database.

    This endpoint is public and does not require authentication, allowing
    even logged-out users to see a health tip.
    """
    # This method is generally more compatible across different SQL databases
    # than ordering by a random function.
    tip_count = db.query(models.Tip).count()
    if tip_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health tips found in the database."
        )

    random_offset = random.randint(0, tip_count - 1)
    random_tip = db.query(models.Tip).offset(random_offset).first()

    if not random_tip:
        # Fallback in case of an issue with the offset.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not retrieve a random health tip."
        )

    return random_tip


@router.post("/", response_model=tip_schema.TipShow, status_code=status.HTTP_201_CREATED)
def create_tip(
    tip: tip_schema.TipCreate,
    db: Session = Depends(get_db)
    # --- Optional Admin Protection ---
    # To make this an admin-only endpoint, you would uncomment the following line
    # and add logic to check if the current_user has admin privileges.
    # current_user: models.User = Depends(get_current_user),
):
    """
    Creates a new health tip in the database.

    In a production application, this endpoint should be protected to ensure
    only authorized administrators can add new tips.
    """
    new_tip = models.Tip(**tip.model_dump())
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)
    return new_tip
