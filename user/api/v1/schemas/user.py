from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr




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
