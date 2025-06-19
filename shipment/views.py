from shipment.api.v1.models.package import Currency
from shipment.api.v1.schemas.shipment import CreateCurrency
from sqlalchemy.orm import Session

class CurrencyService:
    def create_currency(currency_data:CreateCurrency, db: Session):
        currency = currency_data.currency
        if not currency:
            raise Exception("currency is required")
        currency_obj = Currency(currency=currency_data.currency)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj