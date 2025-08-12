# backend/app/routes/user_routes.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Local imports
from .. import models
from ..database import get_db
from ..schemas import user_schema, token_schema
from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)

# --- Authentication Endpoints ---

@router.post("/register", response_model=user_schema.UserShow, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user. Passwords are automatically hashed."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    
    hashed_pwd = hash_password(user.password)
    new_user = models.User(
        full_name=user.full_name, 
        email=user.email, 
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/token", response_model=token_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user and returns a JWT access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- User Profile Management Endpoints ---

@router.get("/me", response_model=user_schema.UserShow)
def read_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """Gets the profile information of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=user_schema.UserShow)
def update_current_user_profile(
    user_update: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates the profile information (name, DOB, address) of the current user."""
    # Convert the Pydantic model to a dictionary, excluding unset values
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.put("/me/password")
def update_current_user_password(
    password_update: user_schema.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates the password for the currently logged-in user."""
    # Verify the current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
    # Hash the new password and update it
    new_hashed_password = hash_password(password_update.new_password)
    current_user.hashed_password = new_hashed_password
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes the account of the currently logged-in user."""
    db.delete(current_user)
    db.commit()
    return None # Return None for 204 No Content status