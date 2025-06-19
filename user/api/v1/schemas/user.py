from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, Field
import re

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


# # Partial update schema (used with PATCH)
class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    hashed_password: Optional[constr(min_length=6)] = Field(None)  # type: ignore
    email: Optional[EmailStr] = Field(None)
    phone_number: Optional[str] = Field(None)
    user_type: Optional[str] = Field(None)

    class Config:
        orm_mode = True


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
        orm_mode = True


# replace
class ReplaceUser(CreateUser):
    pass


from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional


class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)  # type: ignore # ✅ Add minimum length constraint
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        orm_mode = True
