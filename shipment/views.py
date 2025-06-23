from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.status import ShipmentStatus, StatusTracker
from shipment.api.v1.models.shipment import Shipment

# from shipment.api.v1.endpoints.routes import
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.models.shipment import Shipment, ShipmentType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    CreateStatusTracker,
    FetchShipment,
    FetchStatus,
    # ShipmentFilter,
    UpdatePackage,
    UpdateShipment,
    UpdateStatusTracker,
)
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from user.api.v1.models.address import Address
from user.api.v1.models.users import User


# ========================= SHIPMENT SERVICE =========================


class ShipmentService:
    def create_shipment(shipment_data: CreateShipment, db: Session):
        # Validate sender
        sender = db.query(User).filter(User.id == shipment_data.sender_id).first()
        if not sender:
            raise HTTPException(status_code=400, detail="Sender not found")

        # Validate pickup address ownership
        pickup_address_id = (
            db.query(Address)
            .filter(Address.id == shipment_data.pickup_address_id)
            .first()
        )
        if (
            not pickup_address_id
            or pickup_address_id.user_id != shipment_data.sender_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Pickup address does not belong to the sender or does not exist",
            )

        # Validate recipient
        recipient = db.query(User).filter(User.id == shipment_data.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient not found")

        # Validate delivery address ownership
        delivery_address_id = (
            db.query(Address)
            .filter(Address.id == shipment_data.delivery_address_id)
            .first()
        )
        if (
            not delivery_address_id
            or delivery_address_id.user_id != shipment_data.recipient_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Delivery address does not belong to the recipient or does not exist",
            )

        supplier = db.query(User).filter(User.id == shipment_data.recipient_id).first()
        if not supplier:
            raise HTTPException(status_code=400, detail="Recipient not found")

        # Validate shipment type
        try:
            shipment_type = ShipmentType(shipment_data.shipment_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid shipment type: {shipment_data.shipment_type}",
            )

        courier = db.query(User).filter(User.id == shipment_data.courier_id).first()
        if not courier:
            raise HTTPException(status_code=400, detail="Courier not found")

        # Validate package
        package = (
            db.query(Package).filter(Package.id == shipment_data.package_id).first()
        )
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
        shipment_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = (
            db.query(Shipment)
            .options(joinedload(Shipment.packages))
            .filter(Shipment.is_deleted == False)
        )

        # Only join Package if any package-related filter is present
        if any([package_type, currency_id, is_negotiable is not None]):
            query = query.join(Shipment.packages)

            if package_type:
                try:
                    query = query.filter(
                        Package.package_type == PackageType(package_type)
                    )
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid package type")

            if currency_id is not None:
                query = query.filter(Package.currency_id == currency_id)

            if is_negotiable is not None:
                query = query.filter(Package.is_negotiable == is_negotiable)

        if shipment_type:
            query = query.filter(Shipment.shipment_type == shipment_type)

        total = query.distinct().count()
        shipments = query.distinct().offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchShipment.model_validate(s) for s in shipments],
        }

    @staticmethod
    def get_shipment_by_id(shipment_id: int, db: Session):
        shipment = (
            db.query(Shipment)
            .options(joinedload(Shipment.packages))
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )

        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        return FetchShipment.model_validate(shipment)

    # @staticmethod
    # def delete_shipment(shipment_id: int, db: Session):
    #     shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    #     if not shipment:
    #         raise HTTPException(status_code=404, detail="Shipment not found")

    #     shipment.is_deleted = True
    #     db.commit()
    #     return {"message": "Shipment deleted successfully"}

    @staticmethod
    def update_shipment(shipment_id: int, shipment_data: UpdateShipment, db: Session):
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id, Shipment.is_deleted == False).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        for key, value in shipment_data.dict(exclude_unset=True).items():
            setattr(shipment, key, value)

        db.commit()
        db.refresh(shipment)
        return FetchShipment.model_validate(shipment)
    

    def replace_shipment(shipment_id: int, shipment_data: CreateShipment, db: Session):
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id, Shipment.is_deleted == False).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found.")

        for field, value in shipment_data.dict().items():
            setattr(shipment, field, value)

        db.commit()
        db.refresh(shipment)
        return shipment



# ========================= PACKAGE SERVICE =========================


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

    # @staticmethod
    # def disable_package(package_id: int, db: Session):
    #     package = db.query(Package).filter(Package.id == package_id).first()

    #     if not package:
    #         raise HTTPException(status_code=404, detail="Package not found")

    #     if package.is_deleted:
    #         raise HTTPException(status_code=400, detail="Package is already deleted")

    #     package.is_deleted = True

    #     try:
    #         db.commit()
    #         db.refresh(package)
    #     except Exception as e:
    #         db.rollback()
    #         raise HTTPException(
    #             status_code=500, detail=f"Error while deleting package: {str(e)}"
    #         )

    #     return package

    def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id, Package.is_deleted == False).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found.")

        for field, value in package_data.dict(exclude_unset=True).items():
            setattr(package, field, value)

        try:
            db.commit()
            db.refresh(package)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while updating package: {str(e)}"
            )
        return package


# ========================= STATUS TRACKER SERVICE =========================
class StatusTrackerService:
    def create_status_tracker(status_data: CreateStatusTracker, db: Session):
        shipment = (
            db.query(Shipment).filter(Shipment.id == status_data.shipment_id).first()
        )
        if not shipment:
            raise HTTPException(status_code=400, detail="Shipment not found")

        tracker = StatusTracker(
            shipment_id=shipment.id,
            package_id=shipment.package_id,
        )
        db.add(tracker)
        db.commit()
        db.refresh(tracker)
        return tracker

    def get_status(
        db: Session,
        shipment_id: Optional[int] = None,
        package_id: Optional[int] = None,
        status: Optional[ShipmentStatus] = None,
        is_delivered: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        # # Raise error if no filters are provided
        # if not any([shipment_id, package_id, status, is_delivered is not None]):
        #     raise HTTPException(
        #         status_code=400, detail="At least one filter must be provided"
        #     )

        query = db.query(StatusTracker).options(
            joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
        ).filter(StatusTracker.is_deleted == False).first()

        if shipment_id:
            query = query.filter(StatusTracker.shipment_id == shipment_id)

        if package_id:
            query = query.filter(StatusTracker.package_id == package_id)

        if status:
            query = query.filter(StatusTracker.status == status)

        if is_delivered is not None:
            query = query.filter(StatusTracker.is_delivered == is_delivered)

        total = query.distinct().count()
        status_records = query.distinct().offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchStatus.model_validate(s) for s in status_records],
        }

    @staticmethod
    def get_status_by_id(status_id: int, db: Session):
        status_record = (
            db.query(StatusTracker)
            .options(
                joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
            )
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

        if not status_record:
            raise HTTPException(status_code=404, detail="Status record not found")

        return FetchStatus.model_validate(status_record)

    def update_status_tracker(
        status_id: int, status_data: UpdateStatusTracker, db: Session
    ):
        status = db.query(StatusTracker).filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False).first()

        if not status:
            raise HTTPException(status_code=404, detail="Package not found.")

        for field, value in status_data.dict(exclude_unset=True).items():
            setattr(status, field, value)

        try:
            db.commit()
            db.refresh(status)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while updating package: {str(e)}"
            )
        return status

    # def delete_shipment(status_id: int, db: Session):
    #     status = db.query(StatusTracker).filter(StatusTracker.id == status_id).first()
    #     if not status:
    #         raise HTTPException(status_code=404, detail="Status  not found")

    #     status.is_deleted = True
    #     db.commit()
    #     return {"message": "Status deleted successfully"}


# ========================= CURRENCY SERVICE =========================

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
