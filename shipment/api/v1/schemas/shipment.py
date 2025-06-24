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
from shipment.api.v1.models.payment import PaymentMethod, PaymentStatus
from shipment.api.v1.models.shipment import ShipmentType

from shipment.api.v1.models.shipment import ShipmentType
from shipment.api.v1.models.status import ShipmentStatus


# ======================= CURRENCY SCHEMAS =======================


class CreateCurrency(BaseModel):
    currency: str

    class Config:
        from_attributes = True


class FetchCurrency(BaseModel):
    id: int
    currency: str
    is_deleted: bool

    class Config:
        from_attributes = True


class UpdateCurrency(BaseModel):
    currency: Optional[str] = Field(None)
    is_deleted: Optional[bool] = Field(None)

    class Config:
        from_attributes = True


class ReplaceCurrency(BaseModel):
    currency: str
    is_deleted: bool

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
    is_deleted: bool

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateShipment(BaseModel):
    # Sender info
    sender_id: Optional[int] = Field(None)
    sender_name: Optional[str] = Field(None)
    sender_phone: Optional[str] = Field(None)
    sender_email: Optional[EmailStr] = Field(None)

    # Recipient info
    recipient_id: Optional[int] = Field(None)
    recipient_name: Optional[str] = Field(None)
    recipient_phone: Optional[str] = Field(None)
    recipient_email: Optional[EmailStr] = Field(None)

    # Courier and address info
    courier_id: Optional[int] = Field(None)
    pickup_address_id: Optional[int] = Field(None)
    delivery_address_id: Optional[int] = Field(None)

    # Shipment details
    shipment_type: Optional[ShipmentType] = Field(None)

    # Dates
    pickup_date: Optional[datetime] = Field(None)
    delivery_date: Optional[datetime] = Field(None)
    estimated_delivery: Optional[datetime] = Field(None)

    # Extra info
    special_instructions: Optional[str] = Field(None)
    insurance_required: Optional[bool] = Field(None)
    signature_required: Optional[bool] = Field(None)

    # Related package
    package_id: Optional[int] = Field(None)
    is_deleted: Optional[bool] = Field(None)

    class Config:
        from_attributes = True

    
class ReplaceShipment(BaseModel):
    sender_id: int
    sender_name: int
    sender_phone: int
    sender_email: EmailStr
    pickup_address_id: int
    recipient_id: int
    recipient_name: str
    recipient_phone: str
    recipient_email: EmailStr
    delivery_address_id: int
    courier_id: int
    package_id: int
    shipment_type: ShipmentType
    pickup_date: datetime
    delivery_date: datetime
    estimated_delivery: datetime
    special_instructions: str
    insurance_required: bool
    signature_required: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

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
    package_type: PackageType
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    currency_id: int
    is_deleted: bool

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
    is_deleted: Optional[bool] = Field(None)

    class Config:
        from_attributes = True


# ======================= STATUS SCHEMAS =======================


class CreateStatusTracker(BaseModel):
    shipment_id: int

    class Config:
        from_attributes = True


class UpdateStatusTracker(BaseModel):
    shipment_id: Optional[int] = Field(None)
    package_id: Optional[int] = Field(None)
    status: Optional[ShipmentStatus] = Field(None)
    current_location: Optional[str] = Field(None)
    is_delivered: Optional[bool] = Field(None)
    is_deleted: Optional[bool] = Field(None)

    class Config:
        from_attributes = True


class FetchStatus(BaseModel):
    id: int
    shipment_id: int
    package_id: int
    status: ShipmentStatus
    current_location: Optional[str]
    is_delivered: bool
    is_deleted: bool
    updated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ReplaceStatus(BaseModel):
    shipment_id: int
    package_id : int
    status: ShipmentStatus
    current_location: str
    is_delivered: bool
    is_deleted: bool

    class Config:
        from_attributes = True


# ==========payment schema=============


class CreatePayment(BaseModel):
    shipment_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime


class UpdatePayment(BaseModel):
    shipment_id: int = Field(None)
    payment_method: PaymentMethod = Field(None)
    payment_status: PaymentStatus = Field(None)
    payment_date: datetime = Field(None)
    is_deleted: bool = Field(None)


class FetchPayment(BaseModel):
    id: int
    shipment_id: int
    package_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class ReplacePayment(BaseModel):
    shipment_id: int
    package_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
