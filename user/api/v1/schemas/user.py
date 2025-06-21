from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, Field


# ========================= Enums ============================
class UserType(str, Enum):
    importer_exporter = "importer_exporter"
    supplier = "supplier"
    super_admin = "super_admin"


# ===================== User Schemas =========================
class SignUpUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: constr(min_length=6)
    phone_number: str
    user_type: UserType

    model_config = {
        "from_attributes": True
    }


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    phone_number: str
    user_type: UserType

    model_config = {
        "from_attributes": True
    }


class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    hashed_password: Optional[constr(min_length=6)] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ReplaceUser(CreateUser):
    pass  # same fields as CreateUser; placeholder for full PUT update


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

    model_config = {
        "from_attributes": True
    }


# ===================== Auth =========================
class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


# ===================== Address =========================
class CreateAddress(BaseModel):
    user_id: int
    label: Optional[str] = None
    street_address: str
    city: str
    state: str
    postal_code: str
    country_code: int
    landmark: Optional[str] = None
    latitude: float
    longitude: float
    is_default: bool = False

    model_config = {
        "from_attributes": True
    }


class FetchAddress(CreateAddress):
    id: int


# ===================== Country =========================
class CreateCountry(BaseModel):
    name: str

    model_config = {
        "from_attributes": True
    }


class FetchCountry(CreateCountry):
    created_at: Optional[str]
    updated_at: Optional[str]

    model_config = {
        "from_attributes": True
    }
