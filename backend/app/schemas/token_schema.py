# backend/app/schemas/token_schema.py

from typing import Optional

from pydantic import BaseModel


# --- Token Schema ---
class Token(BaseModel):
    """
    Defines the structure of the JSON response when a user successfully logs in.

    This schema is used as the `response_model` for the login endpoint.
    It ensures the API returns the access token and its type in a consistent format.
    """

    access_token: str
    token_type: str


# --- Token Data Schema ---
class TokenData(BaseModel):
    """
    Defines the structure of the data that is encoded *inside* the JWT.

    This schema is used internally within the authentication logic (`auth.py`)
    to validate the contents of a decoded token. It is not directly exposed
    in the API endpoints. It ensures that a decoded token contains the expected
    'subject' field (which we use for the user's email).
    """

    email: Optional[str] = None
