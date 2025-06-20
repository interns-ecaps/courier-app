

from pydantic import BaseModel, Field, constr, EmailStr
from enum import Enum
from shipment.api.v1.models.package import PackageType
from typing import Optional
import re 

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
        orm_mode = True


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
        orm_mode = True


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
        orm_mode = True