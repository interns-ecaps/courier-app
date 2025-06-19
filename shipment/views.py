from shipment.api.v1.models.package import Currency, Package
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage
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
    


class PackageService:
    def create_package(package_data:CreatePackage, db: Session):
        currency_id = package_data.currency_id
        currency = Currency(id=currency_id)
        if not currency:
            raise Exception("currency not found")
        
        package_obj = Package(package_type=package_data.package_type, weight=package_data.weight, length=package_data.length, width=package_data.width, height=package_data.height, is_negotiable=package_data.is_negotiable, currency=currency)
        db.add(package_obj)
        db.commit()
        db.refresh(package_obj)
        return package_obj
    