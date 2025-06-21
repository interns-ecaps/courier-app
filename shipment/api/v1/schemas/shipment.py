

from pydantic import BaseModel, Field, constr, EmailStr
from enum import Enum
from pydantic_settings import BaseSettings
from common.config import settings  # or wherever your config.py is

class Settings(BaseSettings):
    db_name: str
    db_port: int
    secret_key: str

class Config:
        env_file = ".env"

from sqlalchemy import DateTime
from shipment.api.v1.models.package import PackageType
from typing import Optional
import re

from shipment.api.v1.models.shipment import ShipmentType 

from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from shipment.api.v1.models.shipment import ShipmentType

class CreateShipment(BaseModel):
    sender_id: int
    sender_name: str
    sender_phone: str
    sender_email: EmailStr
    pickup_address: int
    recipient_id: int
    recipient_name: str
    recipient_phone: str
    recipient_email: EmailStr
    delivery_address: int
    courier_id: int
    shipment_type: ShipmentType
    package_id: int
    pickup_date: datetime
    special_instructions: Optional[str] = None
    insurance_required: bool
    signature_required: bool



class CreateCurrency(BaseModel):
    currency : str

class CreatePackage(BaseModel):
    package_type : str
    weight : float
    length : float
    width : float
    height : float
    is_negotiable : bool
    currency_id : int
    estimated_cost : Optional[float] = Field(None)
    final_cost : Optional[float] = Field(None)
    
    class Config:
        from_attributes = True


# class PackageTypeEnum(str, Enum):
#     BOX = "box"
#     ENVELOPE = "envelope"
#     PALLET = "pallet"
#     STACKABLE_GOODS = "stackable_goods"  # ✅ Add this line
#     NON_STACKABLE_GOODS = "non_stackable_goods"


class FetchPackage(BaseModel):
    id: int
    package_type: PackageType  # ✅ Use the updated enum here
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    currency_id: int

class Config:
        from_attributes = True

from pydantic import BaseModel

class FetchCurrency(BaseModel):
    id: int
    currency: str

class Config:
    from_attributes = True



class UpdatePackage(BaseModel):
    package_type: Optional[PackageType] = Field(None)
    weight: Optional[float] = Field(None)
    length: Optional[float] = Field(None)
    width: Optional[float] = Field(None)
    height: Optional[float] = Field(None)
    is_negotiable: Optional[bool] = Field(None)
    currency_id: Optional[int] = Field(None)
    estimated_cost: Optional[float] = Field(None)
    final_cost: Optional[float] = Field(None)


    class Config:
        from_attributes = True
