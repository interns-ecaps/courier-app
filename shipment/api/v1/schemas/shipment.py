from pydantic import BaseModel
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