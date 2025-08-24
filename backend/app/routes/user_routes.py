# backend/app/routes/user_routes.py

import os
import shutil
import uuid
from datetime import timedelta
from typing import Optional

from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form,
                     HTTPException, Request, UploadFile, status)
from jose import jwt
from sqlalchemy.orm import Session

from app import models
from app.auth import (create_access_token, get_current_user, hash_password,
                      verify_password)
from app.config import settings
from app.database import get_db
from app.schemas import token_schema, user_schema
from app.utils import create_password_reset_token, send_password_reset_email

# Create a new router for user-related endpoints.
router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)

# --- Constants & Directory Setup ---
UPLOAD_DIRECTORY = "static/profile_pics"
# Create the directory if it doesn't exist on application startup.
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Set a maximum file size for uploads (e.g., 2 MB)
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 Megabytes

# ===================================================================
# --- 1. User Registration & Authentication Endpoints ---
# ===================================================================

@router.post("/register", response_model=user_schema.UserShow, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the database. Passwords are automatically hashed.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email is already registered."
        )

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
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Logs in a user and returns a JWT access token.
    It uses Form data directly to handle the custom 'remember_me' boolean field,
    which is not supported by FastAPI's default OAuth2PasswordRequestForm.

    Args:
        username (str): The user's email.
        password (str): The user's plain text password.
        remember_me (bool): If True, provides a long-lived token.
        db (Session): Database session dependency.
    """
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set the token's expiration time based on the 'remember_me' flag.
    if remember_me:
        expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER)
    else:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=expires_delta
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ===================================================================
# --- 2. Password Reset Endpoints ---
# ===================================================================

@router.post("/forgot-password")
async def forgot_password(
    request: user_schema.ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handles a password reset request.
    Generates a time-limited token and sends a reset email in the background.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    # For security, we don't reveal if the user exists or not.
    # The response is the same in either case.
    if user:
        password_reset_token = create_password_reset_token(email=user.email)
        background_tasks.add_task(
            send_password_reset_email, email=user.email, token=password_reset_token
        )

    return {"message": "If an account with this email exists, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: user_schema.ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets the user's password using a valid token from the reset email.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token. It may be invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("scope") != "password_reset":
            raise credentials_exception
        email: Optional[str] = payload.get("sub")
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

    return {"message": "Your password has been reset successfully."}


# ===================================================================
# --- 3. Profile Photo Upload Endpoint ---
# ===================================================================

@router.post("/me/photo", response_model=user_schema.UserShow)
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads or updates the profile photo for the current user.
    """
    # Validate file extension
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Please use PNG, JPG, or JPEG."
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {MAX_FILE_SIZE / 1024 / 1024} MB."
        )
    # After reading, we must go back to the start of the file stream
    await file.seek(0)

    # Generate a unique filename to prevent conflicts and path traversal.
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # The URL path should be relative to the static mount point.
    url_path = f"/profile_pics/{unique_filename}"
    current_user.profile_picture_url = url_path

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


# ===================================================================
# --- 4. User Profile Management Endpoints ---
# ===================================================================

@router.get("/me", response_model=user_schema.UserShow)
def read_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """
    Gets the profile information of the currently logged-in user.
    """
    return current_user


@router.put("/me", response_model=user_schema.UserShow)
def update_current_user_profile(
    user_update: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Updates the profile information (name, DOB, address, etc.) of the current user.
    """
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
    """
    Updates the password for the currently logged-in user after verifying their current password.
    """
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current password you entered is incorrect."
        )

    new_hashed_password = hash_password(password_update.new_password)
    current_user.hashed_password = new_hashed_password

    db.add(current_user)
    db.commit()

    return {"message": "Password updated successfully."}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deletes the account and all associated data for the currently logged-in user.
    """
    db.delete(current_user)
    db.commit()
    return None
