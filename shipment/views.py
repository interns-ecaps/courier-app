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
    UpdateCurrency,
    # ShipmentFilter,
    UpdatePackage,
    UpdateShipment,
    UpdateStatusTracker,
)
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from user.api.v1.models.address import Address
from user.api.v1.models.users import User
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage
from sqlalchemy.orm import Session
from typing import List, Optional
from shipment.api.v1.models.payment import Payment, PaymentMethod, PaymentStatus
from shipment.api.v1.schemas.shipment import CreatePayment, UpdatePayment


# ======================== CURRENCY SERVICE =========================


class CurrencyService:
    async def create_currency(currency_data: CreateCurrency, db: Session):
        currency = currency_data.currency
        if not currency:
            raise Exception("currency is required")
        currency_obj = Currency(currency=currency_data.currency)
    @staticmethod
    def create_currency(currency_data: CreateCurrency, db: Session):
        print("enter here")
        currency_value = currency_data.currency.strip()
        print(currency_value, "::currency_value")

        if not currency_value:
            raise HTTPException(status_code=400, detail="Currency value cannot be null or empty")

        existing = db.query(Currency).filter(Currency.currency == currency_value).first()
        print(existing, "::existing")
        if existing:
            print("Currency already exists")
            raise HTTPException(status_code=400, detail="Currency already exists")

        currency_obj = Currency(currency=currency_value)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj
       
    
    async def update_currency(currency_id: int, new_data: CreateCurrency, db: Session):
        currency = db.query(Currency).filter(Currency.id == currency_id).first()


    @staticmethod
    def get_currency(db: Session):
        return db.query(Currency).filter(Currency.is_deleted == False).all()

    @staticmethod
    def get_currency_by_id(currency_id: int, db: Session):
        currency = (
            db.query(Currency)
            .filter(Currency.id == currency_id, Currency.is_deleted == False)
            .first()
        )
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        return currency

    def update_currency(currency_id: int, new_data: UpdateCurrency, db: Session):
        currency = (
            db.query(Currency)
            .filter(Currency.id == currency_id, Currency.is_deleted == False)
            .first()
        )
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        existing = db.query(Currency).filter(Currency.name == new_data.currency).first()
        if existing:
            raise HTTPException(status_code=400, detail="Currency already exists")
        if not new_data.currency or new_data.currency.strip() == "":
            raise HTTPException(
                status_code=400, detail="Currency value cannot be null or empty"
            )
        currency.currency = new_data.currency
        db.commit()
        db.refresh(currency)
        return currency
    
    @staticmethod
    async def get_currency_by_id(currency_id: int, db: Session):
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        return currency

    def replace_currency(currency_id: int, new_data: CreateCurrency, db: Session):
        currency = (
            db.query(Currency)
            .filter(Currency.id == currency_id, Currency.is_deleted == False)
            .first()
        )
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        existing = db.query(Currency).filter(Currency.name == new_data.currency).first()
        if existing:
            raise HTTPException(status_code=400, detail="Currency already exists")
        if not new_data.currency or new_data.currency.strip() == "":
            raise HTTPException(
                status_code=400, detail="Currency value cannot be null or empty"
            )
        currency.currency = new_data.currency
        db.commit()
        db.refresh(currency)
        return currency


class ShipmentService:
    def create_shipment(shipment_data: CreateShipment, db: Session):
        # Validate sender
        sender = (
            db.query(User)
            .filter(User.id == shipment_data.sender_id, User.is_deleted == False)
            .first()
        )
        if not sender:
            raise HTTPException(status_code=400, detail="Sender not found")
        sender = sender.filter(User.is_active == True).first()
        if not sender:
            raise HTTPException(status_code=400, detail="Sender not active")

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
        recipient = (
            db.query(User)
            .filter(User.id == shipment_data.recipient_id, User.is_deleted == False)
            .first()
        )
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient not found")
        recipient = recipient.filter(User.is_active == True).first()
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient not active")
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

        # Validate shipment type
        try:
            shipment_type = ShipmentType(shipment_data.shipment_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid shipment type: {shipment_data.shipment_type}",
            )

        courier = (
            db.query(User)
            .filter(User.id == shipment_data.courier_id, User.is_deleted == False)
            .first()
        )
        if not courier:
            raise HTTPException(status_code=400, detail="Courier not found")
        courier = courier.filter(User.is_active == True).first()
        if not courier:
            raise HTTPException(status_code=400, detail="Courier not active")

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
        user_id: Optional[int] = None,
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
        if user_id is not None:
            query = query.filter(User.id == user_id)
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
        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        for key, value in shipment_data.dict(exclude_unset=True).items():
            setattr(shipment, key, value)

        db.commit()
        db.refresh(shipment)
        return FetchShipment.model_validate(shipment)

    def replace_shipment(shipment_id: int, shipment_data: CreateShipment, db: Session):
        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
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


class PaymentService:
    @staticmethod
    async def create_payment(request: CreatePayment, db: Session):
        # Validate shipment
        shipment = db.query(Shipment).filter_by(id=request.shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.shipment_id == request.shipment_id,
                Payment.payment_status == PaymentStatus.COMPLETED,
            )
            .first()
        )

        if existing_payment:
            raise HTTPException(
                status_code=400, detail="Payment already completed for this shipment"
            )
        # Validate package
        # package = db.query(Package).filter_by(id=shipment.package_id).first()
        # if not package:
        #     raise HTTPException(status_code=404, detail="Package not found")

        # @staticmethod
        # def disable_package(package_id: int, db: Session):
        #     package = db.query(Package).filter(Package.id == package_id).first()

        #     if not package:
        #         raise HTTPException(status_code=404, detail="Package not found")

        #     if package.is_deleted:
        #         raise HTTPException(status_code=400, detail="Package is already deleted")

        #     package.is_deleted = True
        payment = Payment(
            shipment_id=request.shipment_id,
            package_id=shipment.package_id,
            payment_method=request.payment_method,
            payment_status=request.payment_status,
            payment_date=request.payment_date,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    async def get_payment_by_id(payment_id: int, db: Session):
        payment = db.query(Payment).filter(Payment.id == payment_id, Payment.is_deleted == False).first()
    def get_payment_by_id(payment_id: int, db: Session):
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id, Payment.is_deleted == False)
            .first()
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    @staticmethod
    async def update_payment(payment_id: int, new_data: UpdatePayment, db: Session):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        if new_data.shipment_id is not None:
            payment.shipment_id = new_data.shipment_id
        if new_data.payment_method is not None:
            payment.payment_method = new_data.payment_method
        if new_data.payment_status is not None:
            payment.payment_status = new_data.payment_status
        if new_data.payment_date is not None:
            payment.payment_date = new_data.payment_date
        if new_data.is_deleted is not None:
            payment.is_deleted = new_data.is_deleted
        db.commit()
        db.refresh(payment)
        return payment

     
        from fastapi import HTTPException


from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    UpdatePackage,
)
from sqlalchemy.orm import Session
from typing import List, Optional


# class CurrencyService:
#     def create_currency(currency_data: CreateCurrency, db: Session):
#         currency = currency_data.currency
#         if not currency:
#             raise Exception("currency is required")
#         currency_obj = Currency(currency=currency_data.currency)
#         db.add(currency_obj)
#         db.commit()
#         db.refresh(currency_obj)
#         return currency_obj


class PackageService:
    async def create_package(package_data: CreatePackage, db: Session):
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
    async def get_packages(
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

    async def get_package_by_id(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
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
    async def disable_package(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_delete:
            raise HTTPException(status_code=400, detail="Package is already deleted")

        package.is_delete = True

    #     try:
    #         db.commit()
    #         db.refresh(package)
    #     except Exception as e:
    #         db.rollback()
    #         raise HTTPException(
    #             status_code=500, detail=f"Error while deleting package: {str(e)}"
    #         )

    #     return package

    async def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        # print(user, "::user")
    def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = (
            db.query(Package)
            .filter(Package.id == package_id, Package.is_deleted == False)
            .first()
        )

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

        query = (
            db.query(StatusTracker)
            .options(
                joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
            )
            .filter(StatusTracker.is_deleted == False)
            .first()
        )

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
        status = (
            db.query(StatusTracker)
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

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
