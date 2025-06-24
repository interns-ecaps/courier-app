from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


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
    password: constr(min_length=6)  # type: ignore
    phone_number: str
    user_type: UserType

    class Config:
        from_attributes = True


# Input for internal user creation (password already hashed)
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    phone_number: str
    user_type: UserType

    class Config:
        from_attributes = True


# # Partial update schema (used with PATCH)
class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    hashed_password: Optional[constr(min_length=6)] = Field(None)  # type: ignore
    email: Optional[EmailStr] = Field(None)
    phone_number: Optional[str] = Field(None)
    user_type: Optional[str] = Field(None)

    class Config:
        from_attributes = True


# # Full user update schema (used with PUT)
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
        from_attributes = True


# replace
class ReplaceUser(CreateUser):
    pass


# class UpdateUser(BaseModel):
#     is_active: bool

#     class Config:
#         from_attributes = True


class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)  # type: ignore # ✅ Add minimum length constraint
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        from_attributes = True


# -----------addresses--------------#
class CreateAddress(BaseModel):
    user_id: int
    label: Optional[str]
    street_address: str
    city: str
    state: str
    postal_code: str
    country_code: int
    landmark: Optional[str] = None
    latitude: float
    longitude: float
    is_default: bool = False

    model_config = {"from_attributes": True}


class FetchAddress(CreateAddress):
    id: int


# ===================== COUNTRIES =====================#


class CreateCountry(BaseModel):
    name: str

    class Config:
        from_attributes = True


class FetchCountry(CreateCountry):
    id: int
    name: str
    is_deleted: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateCountry(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


class ReplaceCountry(BaseModel):
    name: str
    is_deleted: bool

    class Config:
        from_attributes = True
