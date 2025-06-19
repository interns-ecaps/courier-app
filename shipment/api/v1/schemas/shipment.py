<<<<<<< HEAD
from pydantic import BaseModel
class CreateCurrency(BaseModel):
    currency: str
=======


from pydantic import BaseModel
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
>>>>>>> 076e6380fc9b45df87d850187c703f45cd74ebaa
