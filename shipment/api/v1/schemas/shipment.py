from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr
from pydantic_settings import BaseSettings

from common.config import settings
from shipment.api.v1.models.package import PackageType
from shipment.api.v1.models.shipment import ShipmentType


# ======================= CURRENCY SCHEMAS =======================

class CreateCurrency(BaseModel):
    currency: str


class FetchCurrency(BaseModel):
    id: int
    currency: str

    class Config:
        from_attributes = True


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


# ======================= SHIPMENT SCHEMAS =======================

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


class ShipmentFilter(BaseModel):
    package_type: Optional[str] = None
    currency_id: Optional[int] = None
    is_negotiable: Optional[bool] = None
    shipment_type: Optional[str] = None

    class Config:
        from_attributes = True


class FetchShipment(BaseModel):
    id: int
    tracking_number: str

    # Sender info
    sender_id: int
    sender_name: str
    sender_phone: str
    sender_email: Optional[EmailStr]

    # Recipient info
    recipient_id: Optional[int]
    recipient_name: str
    recipient_phone: str
    recipient_email: Optional[EmailStr]

    # Courier and address info
    courier_id: Optional[int]
    pickup_address_id: int
    delivery_address_id: int

    # Shipment details
    shipment_type: ShipmentType

    # Dates
    pickup_date: Optional[datetime]
    delivery_date: Optional[datetime]
    estimated_delivery: Optional[datetime]

    # Extra info
    special_instructions: Optional[str]
    insurance_required: bool
    signature_required: bool

    # Related package
    package_id: int

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateShipment(BaseModel):
    # Sender info
    sender_id: Optional[int]
    sender_name: Optional[str]
    sender_phone: Optional[str]
    sender_email: Optional[EmailStr]

    # Recipient info
    recipient_id: Optional[int]
    recipient_name: Optional[str]
    recipient_phone: Optional[str]
    recipient_email: Optional[EmailStr]

    # Courier and address info
    courier_id: Optional[int]
    pickup_address_id: Optional[int]
    delivery_address_id: Optional[int]

    # Shipment details
    shipment_type: Optional[ShipmentType]

    # Dates
    pickup_date: Optional[datetime]
    delivery_date: Optional[datetime]
    estimated_delivery: Optional[datetime]

    # Extra info
    special_instructions: Optional[str]
    insurance_required: Optional[bool]
    signature_required: Optional[bool]

    # Related package
    package_id: Optional[int]

    class Config:
        from_attributes = True
