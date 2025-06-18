

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class UserType(str, Enum):
    importer_exporter = "importer_exporter"
    supplier = "supplier"
    super_admin = "super_admin"

    
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    hashed_password: str
    email: str
    user_type: str
    phone_number: str

    class Config:
        orm_mode = True
    
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