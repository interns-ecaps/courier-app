from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional


class UserType(str, Enum):
    importer_exporter = "importer_exporter"
    supplier = "supplier"
    super_admin = "super_admin"


# create
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    hashed_password: str
    email: str
    user_type: str
    phone_number: str

    class Config:
        orm_mode = True


# fetch
class FetchUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    user_type: UserType
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


# update
class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    hashed_password: Optional[constr(min_length=6)] = Field(None)
    email: Optional[EmailStr] = Field(None)
    phone_number: Optional[str] = Field(None)
    user_type: Optional[str] = Field(None)


# replace
class ReplaceUser(CreateUser):
    pass
