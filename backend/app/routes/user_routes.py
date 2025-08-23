# backend/app/routes/user_routes.py (Updated with All Features)

### --- NAYE IMPORTS --- ###
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
import shutil
import os
import uuid

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
# Naye utility aur config imports
from ..utils import create_password_reset_token, send_password_reset_email
from ..config import settings


router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)

### --- UPLOAD DIRECTORY SETUP --- ###
UPLOAD_DIRECTORY = "static/profile_pics"
# Directory banayein agar मौजूद nahi hai
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# --- Authentication Endpoints (No Changes) ---

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


### --- PASSWORD RESET ENDPOINTS (NAYA SECTION) --- ###

@router.post("/forgot-password")
async def forgot_password(
    request: user_schema.ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handles password reset request. Generates a token and sends a reset email.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # Security ke liye hum hamesha success message bhejenge
        return {"message": "If an account with this email exists, a reset link has been sent."}

    password_reset_token = create_password_reset_token(email=user.email)
    
    background_tasks.add_task(
        send_password_reset_email, email=user.email, token=password_reset_token
    )
    
    return {"message": "If an account with this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(
    request: user_schema.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resets the user's password using a valid token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token. It may be invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            request.token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("scope") != "password_reset":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Reset token has expired.")
    except jwt.JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    user.hashed_password = hash_password(request.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password has been reset successfully."}


### --- PROFILE PHOTO UPLOAD ENDPOINT (NAYA SECTION) --- ###

@router.post("/me/photo", response_model=user_schema.UserShow)
def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Uploads or updates the profile photo for the current user."""
    
    extension = file.filename.split(".")[-1]
    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format.")
        
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Database mein relative URL path save karein
    url_path = f"/profile_pics/{unique_filename}"
    current_user.profile_picture_url = url_path
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


# --- User Profile Management Endpoints (No Changes) ---

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
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
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
    return None
