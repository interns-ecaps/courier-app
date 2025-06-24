from datetime import datetime
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
    FetchPayment,
    FetchShipment,
    FetchStatus,
    ReplacePayment,
    ReplaceShipment,
    ReplaceStatus,
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
    @staticmethod
    def create_currency(currency_data: CreateCurrency, db: Session):
        print("enter here")
        currency_value = currency_data.currency.strip()
        print(currency_value, "::currency_value")

        if not currency_value:
            raise HTTPException(
                status_code=400, detail="Currency value cannot be null or empty"
            )

        existing = (
            db.query(Currency).filter(Currency.currency == currency_value).first()
        )
        print(existing, "::existing")
        if existing:
            print("Currency already exists")
            raise HTTPException(status_code=400, detail="Currency already exists")

        currency_obj = Currency(currency=currency_value)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj

    @staticmethod
    def get_currency(db: Session, page: int = 1, limit: int = 10):
        query = db.query(Currency).filter(Currency.is_deleted == False)
        total = query.count()
        currencies = query.offset((page - 1) * limit).limit(limit).all()
        return {"page": page, "limit": limit, "total": total, "results": currencies}

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

    def update_currency(currency_id: int, currency_data: UpdateCurrency, db: Session):
        currency = (
            db.query(Currency)
            .filter(Currency.id == currency_id, Currency.is_deleted == False)
            .first()
        )

        if currency_data.is_deleted is not None:
            currency.is_deleted = currency_data.is_deleted

        else:
            if not currency:
                raise HTTPException(status_code=404, detail="Currency not found")
            existing = (
                db.query(Currency)
                .filter(Currency.currency == currency_data.currency)
                .first()
            )
            if existing:
                raise HTTPException(status_code=400, detail="Currency already exists")
            if not currency_data.currency or currency_data.currency.strip() == "":
                raise HTTPException(
                    status_code=400, detail="Currency value cannot be null or empty"
                )
            currency.currency = currency_data.currency
        db.commit()
        db.refresh(currency)
        return currency

    def replace_currency(currency_id: int, new_data: CreateCurrency, db: Session):
        currency = (
            db.query(Currency)
            .filter(Currency.id == currency_id, Currency.is_deleted == False)
            .first()
        )
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        existing = (
            db.query(Currency).filter(Currency.currency == new_data.currency).first()
        )
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


# ==================== SHIPMENT SERVICE =======================


class ShipmentService:
    def create_shipment(shipment_data: CreateShipment, db: Session):
        # Validate sender
        sender = (
            db.query(User)
            .filter(
                User.id == shipment_data.sender_id,
                User.is_deleted == False,
                User.is_active == True,  # <--- moved here
            )
            .first()
        )
        if not sender:
            raise HTTPException(status_code=400, detail="Sender not found or inactive")

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
            .filter(
                User.id == shipment_data.recipient_id,
                User.is_deleted == False,
                User.is_active == True,
            )
            .first()
        )
        if not recipient:
            raise HTTPException(
                status_code=400, detail="Recipient not found or inactive"
            )

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
            .filter(
                User.id == shipment_data.courier_id,
                User.is_deleted == False,
                User.is_active == True,
            )
            .first()
        )
        if not courier:
            raise HTTPException(status_code=400, detail="Courier not found or inactive")

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

    def replace_shipment(shipment_id: int, shipment_data: ReplaceShipment, db: Session):
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


# ========================= STATUS TRACKER SERVICE =========================


class StatusTrackerService:
    def create_status_tracker(request: CreateStatusTracker, db: Session):
        # Validate shipment existence
        shipment = db.query(Shipment).filter_by(id=request.shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Check if a status tracker already exists for this shipment
        existing_tracker = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == request.shipment_id)
            .first()
        )
        if existing_tracker:
            raise HTTPException(
                status_code=400,
                detail="Status tracker already exists for this shipment",
            )

        # Create the tracker
        tracker = StatusTracker(
            shipment_id=request.shipment_id,
            package_id=shipment.package_id,
            status=ShipmentStatus.PENDING,
            current_location=None,
            is_delivered=False,
        )

        db.add(tracker)
        db.commit()
        db.refresh(tracker)
        return tracker

    @staticmethod
    def get_status(
        db: Session,
        shipment_id: Optional[int] = None,
        package_id: Optional[int] = None,
        status: Optional[ShipmentStatus] = None,
        is_delivered: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = (
            db.query(StatusTracker)
            .filter(StatusTracker.is_deleted == False)
            .options(
                joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
            )
        )

        if shipment_id:
            query = query.filter(StatusTracker.shipment_id == shipment_id)

        if package_id:
            query = query.filter(StatusTracker.package_id == package_id)

        if status:
            query = query.filter(StatusTracker.status == status)

        if is_delivered is not None:
            query = query.filter(StatusTracker.is_delivered == is_delivered)

        total = query.count()
        status_records = query.offset((page - 1) * limit).limit(limit).all()

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
            raise HTTPException(status_code=404, detail="Status record not found.")

        # Field-by-field updates
        if status_data.status is not None:
            status.status = status_data.status

        if status_data.current_location is not None:
            status.current_location = status_data.current_location

        if status_data.is_delivered is not None:
            status.is_delivered = status_data.is_delivered

        if status_data.is_deleted is not None:
            status.is_deleted = status_data.is_deleted

        try:
            db.commit()
            db.refresh(status)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while updating status: {str(e)}"
            )

        return status

    def replace_status_tracker(status_id: int, new_data: ReplaceStatus, db: Session):
        status = (
            db.query(StatusTracker)
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

        if not status:
            raise HTTPException(status_code=404, detail="Status record not found")

        # Validate new shipment
        shipment = (
            db.query(Shipment).filter(Shipment.id == new_data.shipment_id).first()
        )
        if not shipment:
            raise HTTPException(status_code=400, detail="Shipment not found")

        # Replace fields
        status.shipment_id = shipment.id
        status.package_id = shipment.package_id
        status.status = ShipmentStatus.PENDING  # Reset to default if needed
        status.current_location = None
        status.is_delivered = False

        db.commit()
        db.refresh(status)
        return status


# ============================PAYMENT SERVICE======================


class PaymentService:
    @staticmethod
    def create_payment(request: CreatePayment, db: Session):
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
    def get_payments(
        db: Session,
        shipment_id: Optional[int] = None,
        package_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        payment_status: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = (
            db.query(Payment)
            .filter(Payment.is_deleted == False)
            .options(joinedload(Payment.shipment), joinedload(Payment.package))
        )

        if shipment_id is not None:
            query = query.filter(Payment.shipment_id == shipment_id)

        if package_id is not None:
            query = query.filter(Payment.package_id == package_id)

        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)

        if payment_status:
            query = query.filter(Payment.payment_status == payment_status)

        if payment_date:
            query = query.filter(Payment.payment_date == payment_date)

        total = query.count()
        payments = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchPayment.model_validate(p) for p in payments],
        }

    @staticmethod
    def get_payment_by_id(payment_id: int, db: Session):
        payment = (
            db.query(Payment)
            .options(joinedload(Payment.shipment), joinedload(Payment.package))
            .filter(Payment.id == payment_id, Payment.is_deleted == False)
            .first()
        )

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        return FetchPayment.model_validate(payment)

    @staticmethod
    def update_payment(payment_id: int, new_data: UpdatePayment, db: Session):
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

    @staticmethod
    def replace_payment(payment_id: int, new_data: ReplacePayment, db: Session):
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id, Payment.is_deleted == False)
            .first()
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Optionally, validate the existence of related shipment
        if new_data.shipment_id is not None:
            shipment = (
                db.query(Shipment).filter(Shipment.id == new_data.shipment_id).first()
            )
            if not shipment:
                raise HTTPException(status_code=400, detail="Shipment not found")
            payment.shipment_id = new_data.shipment_id

        payment.package_id = shipment.package_id
        payment.payment_method = new_data.payment_method
        payment.payment_status = new_data.payment_status
        payment.payment_date = new_data.payment_date

        db.commit()
        db.refresh(payment)
        return payment
