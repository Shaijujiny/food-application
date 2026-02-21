# app/api/auth/schema.py

from pydantic import EmailStr
from app.core.response.base_schema import CustomModel


# ================= REQUEST MODELS =================

class RegisterRequest(CustomModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(CustomModel):
    username: str
    password: str


# ================= RESPONSE DATA MODELS =================

class TokenData(CustomModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileResponse(CustomModel):
    uuid: str
    username: str
    email: str | None = None
    role: str