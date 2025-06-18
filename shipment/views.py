from shipment.api.v1.models.package import Currency
from shipment.api.v1.schemas.currency import CreateCurrency
from sqlalchemy.orm import Session

class CurrencyService:
    def create_currency(currency_data:CreateCurrency, db: Session):
        currency = currency_data.currency
        if not currency:
            raise Exception("currency is required")
        currency_obj = Currency(currency=currency_data)
        return currency_obj