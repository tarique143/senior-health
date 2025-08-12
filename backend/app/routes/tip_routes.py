# backend/app/routes/tip_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import random

from .. import models
from ..database import get_db
from ..schemas import tip_schema
from ..auth import get_current_user # To protect routes if needed

# Create a new router for tips
router = APIRouter(
    prefix="/tips",
    tags=["Health Tips"]
)

@router.get("/random", response_model=tip_schema.TipShow)
def get_random_tip(
    db: Session = Depends(get_db)
):
    """
    Fetches a single random health tip from the database.
    This endpoint is public and does not require authentication.
    """
    # Method 1: Using SQLAlchemy's func.random() (efficient for PostgreSQL)
    random_tip = db.query(models.Tip).order_by(func.random()).first()

    # Method 2: Fetch all and choose randomly (less efficient for large datasets)
    # If the above method gives an error with your DB, you can use this as a fallback.
    # all_tips = db.query(models.Tip).all()
    # if not all_tips:
    #     raise HTTPException(status_code=404, detail="No health tips found in the database.")
    # random_tip = random.choice(all_tips)
    
    if not random_tip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No health tips found in the database.")
    
    return random_tip


@router.post("/", response_model=tip_schema.TipShow, status_code=status.HTTP_201_CREATED)
def create_tip(
    tip: tip_schema.TipCreate, 
    db: Session = Depends(get_db) 
    # Optional: You can protect this route so only an admin can add tips
    # current_user: models.User = Depends(get_current_user) 
):
    """
    Creates a new health tip in the database.
    (This could be an admin-only endpoint in a real application).
    """
    new_tip = models.Tip(**tip.dict())
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)
    return new_tip