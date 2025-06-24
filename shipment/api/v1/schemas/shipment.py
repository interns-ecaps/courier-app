from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, constr, EmailStr
from pydantic_settings import BaseSettings
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr
from pydantic_settings import BaseSettings

from common.config import settings
from shipment.api.v1.models.package import PackageType
from shipment.api.v1.models.shipment import ShipmentType

from shipment.api.v1.models.shipment import ShipmentType
from shipment.api.v1.models.status import ShipmentStatus


# ======================= CURRENCY SCHEMAS =======================



# ======================= SHIPMENT SCHEMAS =======================



# ======================= PACKAGE SCHEMAS ========================


class CreatePackage(BaseModel):
    package_type: PackageType
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    currency_id: int
    estimated_cost: Optional[float] = Field(None)
    final_cost: Optional[float] = Field(None)

    class Config:
        from_attributes = True


class FetchPackage(BaseModel):
    id: int
    package_type: PackageType
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    currency_id: int
    estimated_cost: Optional[float] = None
    final_cost: Optional[float] = None
    is_deleted: bool

    class Config:
        from_attributes = True


class UpdatePackage(BaseModel):
    package_type: Optional[PackageType] = Field(None)
    weight: Optional[float] = Field(None)
    length: Optional[str] = Field(None)
    width: Optional[str] = Field(None)
    height: Optional[str] = Field(None)
    is_negotiable: Optional[bool] = Field(None)
    currency_id: Optional[int] = Field(None)
    estimated_cost: Optional[float] = Field(None)
    final_cost: Optional[float] = Field(None)
    is_deleted: Optional[bool] = Field(None)

    class Config:
        from_attributes = True


class ReplacePackage(BaseModel):
    package_type:str
    weight:float
    length:float
    width:float
    height:float
    is_negotiable:bool
    currency_id:int
    estimated_cost:float
    final_cost:float
    is_deleted:bool



# ======================= STATUS SCHEMAS =======================

# ==========payment schema=============


