from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, constr
from pydantic_settings import BaseSettings
from common.config import settings

from shipment.api.v1.models.package import PackageType
from shipment.api.v1.models.shipment import ShipmentType


class CreateShipment(BaseModel):
    sender_id: int
    sender_name: str
    sender_phone: str
    sender_email: str
    pickup_address_id: int
    recipient_id: int
    recipient_name: str
    recipient_phone: str
    recipient_email: str
    delivery_address_id: int
    courier_id: int
    shipment_type: ShipmentType
    package_id: int
    pickup_date: datetime
    special_instructions: str
    insurance_required: bool
    signature_required: bool

    class Config:
        from_attributes = True


class CreateCurrency(BaseModel):
    currency: str


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

    class Config:
        from_attributes = True


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
