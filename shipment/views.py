from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.status import  ShipmentStatus
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    UpdatePackage,
)
from sqlalchemy.orm import Session
from typing import List, Optional

# class ShipmentService:
#     def create_shipment(shipment_data: CreateShipment, db: Session):
#         new_shipment = Shipment(**shipment_data.dict())
#         db.add(new_shipment)
#         db.commit()
#         db.refresh(new_shipment)
#         return new_shipment

#     def get_shipments(
#         db: Session,
#         package_type: Optional[str] = None,
#         currency_id: Optional[int] = None,
#         is_negotiable: Optional[bool] = None,
#         page: int = 1,
#         limit: int = 10,
#     ):
#         query = db.query(Package).filter(Package.is_deleted == False)

class ShipmentService:
    def create_shipment(shipment_data: CreateShipment, db: Session):
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


from fastapi import HTTPException
from sqlalchemy.orm import Session
from shipment.api.v1.models.shipment import Shipment 
from shipment.api.v1.models.package import Package 
from user.api.v1.models.users import Address
from shipment.api.v1.models.status import (
    StatusTracker,
    ShipmentStatus,
)
from shipment.api.v1.schemas.shipment import (
    CreateStatusTracker,
)  # You need to define this schema


def create_status_tracker(status_data: CreateStatusTracker, db: Session):
    # ✅ Validate foreign key: Shipment
    shipment = db.query(Shipment).filter(Shipment.id == status_data.shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=400, detail="Shipment not found")

    # ✅ Validate foreign key: Package
    package = db.query(Package).filter(Package.id == status_data.package_id).first()
    if not package:
        raise HTTPException(status_code=400, detail="Package not found")

    # ✅ Validate Enum
    try:
        status_enum = ShipmentStatus(status_data.status)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid status: {status_data.status}"
        )

    # ✅ Create object
    tracker = StatusTracker(
        shipment_id=status_data.shipment_id,
        package_id=status_data.package_id,
        status=status_enum,
        current_location=status_data.current_location,
        is_delivered=status_data.is_delivered or False,
    )

    db.add(tracker)
    db.commit()
    db.refresh(tracker)
    return tracker
