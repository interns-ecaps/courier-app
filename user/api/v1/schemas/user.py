from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


# Enum for user roles
class UserType(str, Enum):
    importer_exporter = "importer_exporter"
    supplier = "supplier"
    super_admin = "super_admin"


# Input when user signs up (includes raw password)
class SignUpUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: constr(min_length=6)
    phone_number: str
    user_type: UserType

    class Config:
        orm_mode = True


# Input for internal user creation (password already hashed)
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    phone_number: str
    user_type: UserType

    class Config:
        orm_mode = True


# Partial update schema (used with PATCH)
class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    hashed_password: Optional[constr(min_length=6)] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    user_type: Optional[UserType] = None

    class Config:
        orm_mode = True


# Full user update schema (used with PUT)
class ReplaceUser(CreateUser):
    pass  # exact same fields as CreateUser; can extend later if needed


# Output schema for fetching user data
class FetchUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    user_type: UserType
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Auth token response schema
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


# Token payload schema
class TokenData(BaseModel):
    username: Optional[str] = None  # or `user_id: Optional[int]` if using ID in token
