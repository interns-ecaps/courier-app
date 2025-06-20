from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    UpdatePackage,
)
from sqlalchemy.orm import Session
from typing import List, Optional


class CurrencyService:
    def create_currency(currency_data: CreateCurrency, db: Session):
        currency = currency_data.currency
        if not currency:
            raise Exception("currency is required")
        currency_obj = Currency(currency=currency_data.currency)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj


class PackageService:
    def create_package(package_data: CreatePackage, db: Session):
        # currency_id = package_data.currency_id
        currency = (
            db.query(Currency).filter(Currency.id == package_data.currency_id).first()
        )
        if not currency:
            raise HTTPException(status_code=400, detail="Currency not found")

        try:
            package_type_enum = PackageType(package_data.package_type)
        except ValueError:
            raise Exception(f"Invalid package_type: {package_data.package_type}")

        package_obj = Package(
            package_type=package_type_enum,
            weight=package_data.weight,
            length=package_data.length,
            width=package_data.width,
            height=package_data.height,
            is_negotiable=package_data.is_negotiable,
            currency=currency,
        )
        db.add(package_obj)
        db.commit()
        db.refresh(package_obj)
        return package_obj

    @staticmethod
    def get_packages(
        db: Session,
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = db.query(Package)

        if package_type:
            try:
                query = query.filter(Package.package_type == PackageType(package_type))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid package_type")

        if currency_id:
            query = query.filter(Package.currency_id == currency_id)

        if is_negotiable is not None:
            query = query.filter(Package.is_negotiable == is_negotiable)

        total = query.count()
        results = query.offset((page - 1) * limit).limit(limit).all()

        return {"page": page, "limit": limit, "total": total, "results": results}

    def get_package_by_id(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        return package
    
class CurrencyService:
    @staticmethod
    def create_currency(currency_data: CreateCurrency, db: Session):
        if not currency_data.currency:
            raise HTTPException(status_code=400, detail="Currency is required")

        currency_obj = Currency(currency=currency_data.currency)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj

    @staticmethod
    def get_currencies(db: Session):
        return db.query(Currency).all()

    @staticmethod
    def get_currency_by_id(currency_id: int, db: Session):
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        return currency

        
    @staticmethod
    def disable_package(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Package not found.")

        package.is_delete = True

    def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        # print(user, "::user")

        if not package:
            raise HTTPException(status_code=404, detail="Package not found.")

        for field, value in package_data.dict(exclude_unset=True).items():
            setattr(package, field, value)

        db.commit()
        db.refresh(package)
        return package
