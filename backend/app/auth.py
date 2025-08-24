# backend/app/auth.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db
from app.schemas import token_schema

# --- Password Hashing ---
# We use bcrypt as the hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Scheme ---
# This defines the security scheme. `tokenUrl` points to the login endpoint
# that the client will use to get the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches its hashed version.

    Args:
        plain_password: The password in plain text.
        hashed_password: The hashed password from the database.

    Returns:
        True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password: The password to hash.

    Returns:
        The hashed password as a string.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data: The data to encode in the token (e.g., user email).
        expires_delta: An optional timedelta to specify token expiry.
                       If None, a default expiry is used from settings.

    Returns:
        The encoded JWT as a string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # If no specific expiry time is provided, use the default from settings.
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current user from a JWT token.

    This function is used in path operations to protect routes and identify
    the currently authenticated user.

    Args:
        token: The bearer token from the request's Authorization header.
        db: The database session dependency.

    Raises:
        HTTPException (401): If the token is invalid, expired, or the user
                             is not found.

    Returns:
        The SQLAlchemy User model instance for the authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token using the secret key and algorithm from settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = token_schema.TokenData(email=email)
    except JWTError:
        # This catches errors like invalid signature, malformed token, etc.
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == token_data.email).first()

    if user is None:
        # This case handles a valid token for a user that has since been deleted.
        raise credentials_exception

    return user
