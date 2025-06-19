from pydantic import BaseModel
class CreateCurrency(BaseModel):
    currency: str