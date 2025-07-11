from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, constr, EmailStr
from pydantic_settings import BaseSettings
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

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
    currency: Annotated[
        str,
        Field(
            min_length=3,
            max_length=3,
            pattern=r"^[A-Z]{3}$",
            description="3-letter ISO currency code (e.g., USD, INR)",
        ),
    ]

    model_config = {"from_attributes": True}


class FetchCurrency(BaseModel):
    id: Annotated[int, Field(description="Currency ID")]
    currency: Annotated[str, Field(description="3-letter currency code")]
    is_deleted: Annotated[bool, Field(description="Soft-deletion status")]

    model_config = {"from_attributes": True}


class UpdateCurrency(BaseModel):
    currency: Optional[
        Annotated[
            str,
            Field(
                min_length=3,
                max_length=3,
                pattern=r"^[A-Z]{3}$",
                description="Updated currency code (3 uppercase letters)",
            ),
        ]
    ] = None

    is_deleted: Optional[
        Annotated[bool, Field(description="Mark currency as deleted or restored")]
    ] = None

    model_config = {"from_attributes": True}


class ReplaceCurrency(BaseModel):
    currency: Annotated[
        str,
        Field(
            min_length=3,
            max_length=3,
            pattern=r"^[A-Z]{3}$",
            description="New currency code (3 uppercase letters)",
        ),
    ]
    is_deleted: Annotated[bool, Field(description="Soft-delete flag")]

    model_config = {"from_attributes": True}


# ======================= SHIPMENT SCHEMAS =======================


class CreateShipment(BaseModel):
    pickup_address_id: Annotated[
        int, Field(gt=0, description="ID of the pickup address")
    ]
    # pickup_address_text: Optional[str] = Field(None, description="Free-text pickup address (optional)")

    recipient_name: Annotated[
        str, Field(min_length=2, max_length=100, description="Recipient's full name")
    ]

    recipient_phone: Annotated[
        str, Field(description="Recipient's phone number")
    ]
    
    recipient_email: Annotated[
        EmailStr,
        Field(description="Recipient's email address (used to fetch user record)"),
    ]
    
    delivery_address_text: Optional[str] = Field(None, description="Free-text delivery address")

    courier_id: Annotated[
        int, Field(gt=0, description="Courier user ID assigned to the shipment")
    ]

    shipment_type: Annotated[
        ShipmentType,
        Field(description="Type of shipment: standard, express, overnight, same_day"),
    ]
    package_id: Annotated[
        int, Field(gt=0, description="Package ID linked to the shipment")
    ]

    pickup_date: Annotated[datetime, Field(description="Pickup datetime")]
    special_instructions: Annotated[
        Optional[str],
        Field(max_length=500, description="Any special instructions for delivery"),
    ]
    insurance_required: Annotated[
        bool, Field(description="Whether insurance is required")
    ]
    signature_required: Annotated[
        bool, Field(description="Whether recipient signature is required")
    ]

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
    recipient_name: str
    recipient_phone: str
    recipient_email: Optional[EmailStr]

    # Courier and address info
    courier_id: Optional[int]
    pickup_address_id: int
    
    # Delivery address (free-text)
    delivery_address_text: Optional[str] = None

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

    package_id: int
    is_deleted: bool

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    latest_status: Optional[str] = None
    payment_status: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateShipment(BaseModel):
    sender_id: Optional[int] = Field(
        None, gt=0, description="Updated sender user ID (optional)"
    )
    sender_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Sender name (2-100 characters)"
    )
    sender_phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r"^\+?[0-9\- ]{7,20}$",
        description="Sender phone number (digits, spaces, dashes, optional +)",
    )
    sender_email: Optional[EmailStr] = Field(
        None, description="Sender's email (optional)"
    )

    recipient_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Recipient name (2-100 characters)",
    )
    recipient_phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r"^\+?[0-9\- ]{7,20}$",  # ✅ correct
        description="Sender phone number (digits, spaces, dashes, optional +)",
    )

    recipient_email: Optional[EmailStr] = Field(
        None, description="Recipient's email (optional)"
    )

    courier_id: Optional[int] = Field(
        None, gt=0, description="Courier user ID (optional)"
    )
    pickup_address_id: Optional[int] = Field(
        None, gt=0, description="Pickup address ID (optional)"
    )

    shipment_type: Optional[ShipmentType] = Field(
        None, description="Updated shipment type (optional)"
    )

    pickup_date: Optional[datetime] = Field(None, description="Updated pickup datetime")
    delivery_date: Optional[datetime] = Field(
        None, description="Updated delivery datetime"
    )
    estimated_delivery: Optional[datetime] = Field(
        None, description="Updated estimated delivery datetime"
    )

    special_instructions: Optional[str] = Field(
        None, max_length=500, description="Updated delivery instructions"
    )
    insurance_required: Optional[bool] = Field(
        None, description="Update insurance requirement flag"
    )
    signature_required: Optional[bool] = Field(
        None, description="Update signature requirement flag"
    )

    package_id: Optional[int] = Field(
        None, gt=0, description="Updated package ID (optional)"
    )
    is_deleted: Optional[bool] = Field(None, description="Mark shipment as deleted")

    class Config:
        from_attributes = True


class ReplaceShipment(BaseModel):
    sender_id: Annotated[int, Field(gt=0, description="Sender user ID")]
    sender_name: Annotated[
        str, Field(min_length=2, max_length=100, description="Sender's full name")
    ]
    sender_phone: Annotated[
        str,
        Field(
            pattern=r"^\+?[0-9\- ]{7,20}$",
            max_length=20,
            description="Sender's phone number",
        ),
    ]
    sender_email: Annotated[EmailStr, Field(description="Sender's email address")]

    pickup_address_id: Annotated[int, Field(gt=0, description="Pickup address ID")]

    recipient_name: Annotated[
        str, Field(min_length=2, max_length=100, description="Recipient's full name")
    ]
    recipient_phone: Annotated[
        str,
        Field(
            pattern=r"^\+?[0-9\- ]{7,20}$",
            max_length=20,
            description="Recipient's phone number",
        ),
    ]
    recipient_email: Annotated[EmailStr, Field(description="Recipient's email address")]

    courier_id: Annotated[int, Field(gt=0, description="Assigned courier user ID")]
    package_id: Annotated[int, Field(gt=0, description="Linked package ID")]

    shipment_type: Annotated[ShipmentType, Field(description="Type of shipment")]

    pickup_date: Annotated[
        datetime, Field(description="Scheduled pickup date and time")
    ]
    delivery_date: Annotated[
        datetime, Field(description="Actual delivery date and time")
    ]
    estimated_delivery: Annotated[
        datetime, Field(description="Estimated delivery datetime")
    ]

    special_instructions: Annotated[
        Optional[str], Field(max_length=500, description="Delivery instructions")
    ]
    insurance_required: Annotated[bool, Field(description="Insurance required flag")]
    signature_required: Annotated[bool, Field(description="Signature required flag")]
    is_deleted: Annotated[bool, Field(description="Soft delete flag")]

    class Config:
        from_attributes = True


# ======================= PACKAGE SCHEMAS ========================


class CreatePackage(BaseModel):
    package_type: PackageType
    weight: float = Field(..., gt=0, description="Package weight in kg")
    length: float = Field(..., gt=0, description="Package length in cm")
    width: float = Field(..., gt=0, description="Package width in cm")
    height: float = Field(..., gt=0, description="Package height in cm")
    is_negotiable: bool
    currency_id: int = Field(..., gt=0, description="Valid currency ID")
    estimated_cost: Optional[float] = Field(
        None, ge=0, description="Estimated cost if known"
    )
    final_cost: Optional[float] = Field(None, ge=0, description="Final cost if known")

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
    package_type: Optional[PackageType] = None
    weight: Optional[float] = Field(None, gt=0)
    length: Optional[float] = Field(None, gt=0)
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    is_negotiable: Optional[bool] = None
    currency_id: Optional[int] = Field(None, gt=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    final_cost: Optional[float] = Field(None, ge=0)
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


class ReplacePackage(BaseModel):
    package_type: PackageType
    weight: float = Field(..., gt=0)
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    is_negotiable: bool
    currency_id: int = Field(..., gt=0)
    estimated_cost: float = Field(..., ge=0)
    final_cost: float = Field(..., ge=0)
    is_deleted: bool

    class Config:
        from_attributes = True


# ======================= STATUS SCHEMAS =======================


from pydantic import BaseModel, Field


class CreateStatusTracker(BaseModel):
    shipment_id: int = Field(..., gt=0, description="Associated shipment ID")

    class Config:
        from_attributes = True


from typing import Optional


class UpdateStatusTracker(BaseModel):
    shipment_id: Optional[int] = Field(None, gt=0, description="Updated shipment ID")
    package_id: Optional[int] = Field(None, gt=0, description="Updated package ID")
    status: Optional[ShipmentStatus] = Field(
        None, description="Current shipment status"
    )
    current_location: Optional[str] = Field(
        None, max_length=255, description="Current location of the shipment"
    )
    is_delivered: Optional[bool] = Field(None, description="Delivery status")
    is_deleted: Optional[bool] = Field(None, description="Soft deletion flag")

    class Config:
        from_attributes = True


from datetime import datetime


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
    shipment_id: int = Field(..., gt=0, description="Shipment ID")
    package_id: int = Field(..., gt=0, description="Package ID")
    status: ShipmentStatus = Field(..., description="Shipment status")
    current_location: str = Field(..., max_length=255, description="Current location")
    is_delivered: bool = Field(..., description="Whether the package is delivered")
    is_deleted: bool = Field(..., description="Soft delete flag")

    class Config:
        from_attributes = True


# ==========payment schema=============


class CreatePayment(BaseModel):
    shipment_id: Annotated[int, Field(gt=0, description="Associated shipment ID")]
    payment_method: Annotated[PaymentMethod, Field(description="Payment method used")]
    payment_status: Annotated[
        PaymentStatus, Field(description="Current status of payment")
    ]
    payment_date: Annotated[datetime, Field(description="Date of payment")]

    class Config:
        from_attributes = True


class UpdatePayment(BaseModel):
    shipment_id: Optional[Annotated[int, Field(gt=0)]] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    payment_date: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


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
    shipment_id: Annotated[int, Field(gt=0)]
    package_id: Annotated[int, Field(gt=0)]
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: Annotated[datetime, Field(description="Date the payment was made")]
    is_deleted: bool

    class Config:
        from_attributes = True


class PackageOut(BaseModel):
    id: int
    label: str
    final_cost: float
    type: str
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    estimated_cost: float = None
    currency: str = None

class ShipmentOut(BaseModel):
    id: int
    package: PackageOut
    payment_status: Optional[str] = None
    # ... add other fields as needed
