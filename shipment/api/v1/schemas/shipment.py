from pydantic import BaseModel
from datetime import datetime
from enum import Enum
class CreateCurrency(BaseModel):
    currency: str


from pydantic import BaseModel
from enum import Enum
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
    
    class Config:
        orm_mode = True


class PackageTypeEnum(str, Enum):
    BOX = "box"
    ENVELOPE = "envelope"
    PALLET = "pallet"
    STACKABLE_GOODS = "stackable_goods"  # ✅ Add this line
    NON_STACKABLE_GOODS = "non_stackable_goods"


class FetchPackage(BaseModel):
    id: int
    package_type: PackageTypeEnum  # ✅ Use the updated enum here
    weight: float
    length: float
    width: float
    height: float
    is_negotiable: bool
    currency_id: int

    class Config:
        orm_mode = True
class PaymentMethod(str, Enum):
    CASH = "CASH"
    ONLINE = "ONLINE"
    WIRE_TRANSFER = "WIRE_TRANSFER"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CreatePayment(BaseModel):
    shipment_id: int
    package_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime

class UpdatePayment(BaseModel):
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime

class FetchPayment(BaseModel):
    id: int
    shipment_id: int
    package_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_date: datetime

    class Config:
        orm_mode = True