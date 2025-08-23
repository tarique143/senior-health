# backend/app/routes/user_routes.py (Updated for "Remember Me")

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Request
from sqlalchemy.orm import Session
from jose import jwt
import shutil
import os
import uuid
from datetime import timedelta # Yeh naya import hai

# Absolute imports from the 'app' package root
from app import models
from app.database import get_db
from app.schemas import user_schema, token_schema
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from app.utils import create_password_reset_token, send_password_reset_email
from app.config import settings

router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)

# --- Upload Directory Setup ---
UPLOAD_DIRECTORY = "static/profile_pics"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


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

### --- LOGIN ENDPOINT MEIN BADLAV --- ###
@router.post("/token", response_model=token_schema.Token)
async def login_for_access_token(request: Request, db: Session = Depends(get_db)):
    """
    Logs in a user and returns a JWT access token.
    Handles 'remember_me' to provide a long-lived token.
    """
    # Hum 'request.form()' ka istemal kar rahe hain taaki 'remember_me' field ko bhi le sakein
    # OAuth2PasswordRequestForm iski anumati nahi deta
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    # Frontend se "true" (string) aayega. Usse boolean mein convert karein.
    remember_me = form_data.get("remember_me", "false").lower() == "true"

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Expiry time set karein
    if remember_me:
        expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER)
    else:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": user.email}, expires_delta=expires_delta)
    
    return {"access_token": access_token, "token_type": "bearer"}
### --- LOGIN ENDPOINT MEIN BADLAV (END) --- ###


# --- Password Reset Endpoints ---
@router.post("/forgot-password")
async def forgot_password(
    request: user_schema.ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handles password reset request. Generates a token and sends a reset email."""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    # Don't reveal if the user exists or not for security reasons
    if user:
        password_reset_token = create_password_reset_token(email=user.email)
        background_tasks.add_task(
            send_password_reset_email, email=user.email, token=password_reset_token
        )
    
    return {"message": "If an account with this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: user_schema.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Resets the user's password using a valid token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token. It may be invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("scope") != "password_reset": raise credentials_exception
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Reset token has expired.")
    except jwt.JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise credentials_exception

    user.hashed_password = hash_password(request.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password has been reset successfully."}


# --- Profile Photo Upload Endpoint ---
@router.post("/me/photo", response_model=user_schema.UserShow)
def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Uploads or updates the profile photo for the current user."""
    extension = file.filename.split(".")[-1].lower()
    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format. Please use PNG, JPG, or JPEG.")
        
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    url_path = f"/profile_pics/{unique_filename}"
    current_user.profile_picture_url = url_path
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


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
    """Updates the profile information of the current user."""
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
