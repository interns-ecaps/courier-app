from email.headerregistry import Address
from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.status import  ShipmentStatus
from shipment.api.v1.models.shipment import Shipment, ShipmentType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    UpdatePackage,
)
from sqlalchemy.orm import Session
from typing import List, Optional

from user.api.v1.models.users import User


class ShipmentService:
    def create_shipment(shipment_data: CreateShipment, db: Session):
        # Validate sender
        sender = db.query(User).filter(User.id == shipment_data.sender_id).first()
        if not sender:
            raise HTTPException(status_code=400, detail="Sender not found")
    
        # Validate pickup address ownership
        pickup_address = db.query(Address).filter(Address.id == shipment_data.pickup_address).first()
        if not pickup_address or pickup_address.user_id != shipment_data.sender_id:
            raise HTTPException(
                status_code=400,
                detail="Pickup address does not belong to the sender or does not exist"
            )

        # Validate recipient
        recipient = db.query(User).filter(User.id == shipment_data.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient not found")

        # Validate delivery address ownership
        delivery_address = db.query(Address).filter(Address.id == shipment_data.delivery_address).first()
        if not delivery_address or delivery_address.user_id != shipment_data.recipient_id:
            raise HTTPException(
                status_code=400,
                detail="Delivery address does not belong to the recipient or does not exist"
            )
            
        supplier = (
            db.query(User).filter(User.id == shipment_data.recipient_id).first()
        )
        if not supplier:
            raise HTTPException(status_code=400, detail="Recipient not found")
        
        # Validate shipment type
        try:
            shipment_type = ShipmentType(shipment_data.shipment_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid shipment type: {shipment_data.shipment_type}"
            )
        
        courier = db.query(User).filter(User.id == shipment_data.courier_id).first()
        if not courier:
            raise HTTPException(status_code=400, detail="Courier not found")

        # Validate package
        package = db.query(Package).filter(Package.id == shipment_data.package_id).first()
        if not package:
            raise HTTPException(status_code=400, detail="Package not found")

        new_shipment = Shipment(**shipment_data.dict())
        db.add(new_shipment)
        db.commit()
        db.refresh(new_shipment)
        return new_shipment

    def get_shipments(
        db: Session,
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = db.query(Package).filter(Package.is_deleted == False)

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
        query = db.query(Package).filter(Package.is_deleted == False)

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
        package = (
            db.query(Package)
            .filter(Package.id == package_id, Package.is_deleted == False)
            .first()
        )
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
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_deleted:
            raise HTTPException(status_code=400, detail="Package is already deleted")

        package.is_deleted = True

        try:
            db.commit()
            db.refresh(package)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while deleting package: {str(e)}"
            )

        return package

    def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        # print(user, "::user")

        if not package:
            raise HTTPException(status_code=404, detail="Package not found.")

        for field, value in package_data.dict(exclude_unset=True).items():
            setattr(package, field, value)

        try:
            db.commit()
            db.refresh(package)  # optional — to return the updated version
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while updating package: {str(e)}"
            )
        return package
