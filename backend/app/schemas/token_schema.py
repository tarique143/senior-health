# backend/app/schemas/token_schema.py

from pydantic import BaseModel
from typing import Optional

# --- Token Schemas ---

# This schema defines the structure of the response
# when a user successfully logs in and receives a token.
class Token(BaseModel):
    access_token: str
    token_type: str

# This schema defines the structure of the data
# that is encoded inside the JWT token.
class TokenData(BaseModel):
    email: Optional[str] = None