from datetime import datetime
from fastapi import HTTPException, status
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
    FetchPackage,
    FetchPayment,
    FetchShipment,
    FetchStatus,
    ReplacePackage,
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
    async def create_currency(request, currency_data: CreateCurrency, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can create currencies"
            )

        currency_value = currency_data.currency.strip()


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
    async def get_currency(request, db: Session, page: int = 1, limit: int = 10):
        query = db.query(Currency).filter(Currency.is_deleted == False)
        total = query.count()
        currencies = query.offset((page - 1) * limit).limit(limit).all()
        return {"page": page, "limit": limit, "total": total, "results": currencies}

    @staticmethod
    # async def get_currency_by_id(currency_id: int, db: Session):
    #     currency = (
    #         db.query(Currency)
    #         .filter(Currency.id == currency_id, Currency.is_deleted == False)
    #         .first()
    #     )
    #     if not currency:
    #         raise HTTPException(status_code=404, detail="Currency not found")
    #     return currency

    async def update_currency(
        request, currency_id: int, currency_data: UpdateCurrency, db: Session
    ):

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can edit currencies"
            )

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

    async def replace_currency(
        request, currency_id: int, new_data: CreateCurrency, db: Session
    ):

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can edit currencies"
            )

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
    @staticmethod
    async def create_shipment(request, shipment_data: CreateShipment, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate pickup address ownership
        pickup_address = (
            db.query(Address)
            .filter(
                Address.id == shipment_data.pickup_address_id,
                Address.user_id == user_obj.id,
                Address.is_deleted == False,
            )
            .first()
        )

        if not pickup_address:
            raise HTTPException(
                status_code=400,
                detail="Pickup address does not belong to the sender or does not exist",
            )

        # Fetch recipient by ID or email
        recipient = None
        # if shipment_data.recipient_id:
        #     recipient = db.query(User).filter(
        #         User.id == shipment_data.recipient_id,
        #         User.is_deleted == False,
        #         User.is_active == True
        #     ).first()
        # el
        if shipment_data.recipient_email:
            recipient = (
                db.query(User)
                .filter(
                    User.email == shipment_data.recipient_email,
                    User.is_deleted == False,
                    User.is_active == True,
                )
                .first()
            )

        if not recipient:
            raise HTTPException(
                status_code=404, detail="Recipient not found or inactive"
            )

        # Validate delivery address
        delivery_address = (
            db.query(Address)
            .filter(
                Address.id == shipment_data.delivery_address_id,
                Address.user_id == recipient.id,
                Address.is_deleted == False,
            )
            .first()
        )

        if not delivery_address:
            raise HTTPException(
                status_code=400,
                detail="Delivery address does not belong to the recipient or does not exist",
            )

        # Validate courier
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
            db.query(Package)
            .filter(
                Package.id == shipment_data.package_id,
                Package.user_id == user_obj.id,
                Package.is_deleted == False,
            )
            .first()
        )
        if not package:
            raise HTTPException(
                status_code=400,
                detail="Package not found or does not belong to the sender",
            )

        # Validate shipment type
        try:
            shipment_type = ShipmentType(shipment_data.shipment_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid shipment type: {shipment_data.shipment_type}",
            )

        # Construct shipment record
        new_shipment = Shipment(
            sender_id=user_obj.id,
            sender_name=user_obj.first_name + " " + user_obj.last_name,
            sender_phone=user_obj.phone_number,
            sender_email=user_obj.email,
            pickup_address_id=shipment_data.pickup_address_id,
            recipient_id=recipient.id,
            recipient_name=recipient.first_name + " " + recipient.last_name,
            recipient_phone=recipient.phone_number,
            recipient_email=recipient.email,
            delivery_address_id=shipment_data.delivery_address_id,
            courier_id=shipment_data.courier_id,
            shipment_type=shipment_type,
            package_id=shipment_data.package_id,
            pickup_date=shipment_data.pickup_date,
            special_instructions=shipment_data.special_instructions,
            insurance_required=shipment_data.insurance_required,
            signature_required=shipment_data.signature_required,
        )

        db.add(new_shipment)
        db.commit()

        await StatusTrackerService.create_status_tracker(
            request=request,
            request_data=CreateStatusTracker(shipment_id=new_shipment.id),
            db=db,
        )

        db.refresh(new_shipment)
        return new_shipment

    async def get_shipments(
        request,
        db: Session,
        user_id: Optional[int] = None,
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        shipment_type: Optional[str] = None,
        pickup_from: Optional[datetime] = None,
        pickup_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10,
    ):
        # Get signed-in user
        requester_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User)
            .filter(User.id == requester_id, User.is_deleted == False)
            .first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # # Start base query
        # query = db.query(Shipment).filter(Shipment.is_deleted == False)

        if user_obj.user_type == "super_admin":
            query = db.query(Shipment).filter(Shipment.is_deleted == False)
        else:
            query = db.query(Shipment).filter(
                Shipment.sender_id == user_obj.id, Shipment.is_deleted == False
            )
        # Optional filter: shipment type
        if shipment_type:
            try:
                query = query.filter(
                    Shipment.shipment_type == ShipmentType(shipment_type)
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid shipment type")

        # Pickup date range filters
        if pickup_from and pickup_to:
            query = query.filter(Shipment.pickup_date.between(pickup_from, pickup_to))
        elif pickup_from:
            query = query.filter(Shipment.pickup_date >= pickup_from)
        elif pickup_to:
            query = query.filter(Shipment.pickup_date <= pickup_to)

        # Package-related filters
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

        if user_id:
            query = query.filter(Shipment.sender_id == user_id)

        # Fetch results with pagination
        total = query.distinct().count()
        shipments = query.distinct().offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchShipment.model_validate(s) for s in shipments],
        }

    @staticmethod
    async def get_shipment_by_id(shipment_id: int, db: Session):
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
    async def update_shipment(
        request, shipment_id: int, shipment_data: UpdateShipment, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # If not super admin, check if this user owns the shipment
        if user_obj.user_type != "super_admin" and shipment.sender_id != user_obj.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this shipment",
            )

        # Validate that the package (if updated) still belongs to the sender
        if shipment_data.package_id:
            package = (
                db.query(Package)
                .filter(
                    Package.id == shipment_data.package_id,
                    Package.sender_id == shipment.sender_id,
                    Package.is_deleted == False,
                )
                .first()
            )
            if not package:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid package: either not found or doesn't belong to the sender",
                )

        # Apply updates
        for key, value in shipment_data.dict(exclude_unset=True).items():
            setattr(shipment, key, value)

        db.commit()
        db.refresh(shipment)

        return FetchShipment.model_validate(shipment)

    async def replace_shipment(
        request, shipment_id: int, shipment_data: ReplaceShipment, db: Session
    ):
        # 1. Authenticated user check
        user_id = request.state.user.get("sub")
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Find shipment
        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found.")

        # 3. Only sender or super admin can replace
        if user_obj.user_type != "super_admin" and shipment.sender_id != user_obj.id:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 4. Validate users
        for role, uid in [
            ("sender", shipment_data.sender_id),
            ("recipient", shipment_data.recipient_id),
            ("courier", shipment_data.courier_id),
        ]:
            user = (
                db.query(User)
                .filter(
                    User.id == uid, User.is_active == True, User.is_deleted == False
                )
                .first()
            )
            if not user:
                raise HTTPException(status_code=400, detail=f"Invalid {role} user")

        # 5. Validate pickup address belongs to sender
        pickup_address = (
            db.query(Address)
            .filter(
                Address.id == shipment_data.pickup_address_id,
                Address.user_id == shipment_data.sender_id,
                Address.is_deleted == False,
            )
            .first()
        )
        if not pickup_address:
            raise HTTPException(status_code=400, detail="Invalid pickup address")

        # 6. Validate delivery address belongs to recipient
        delivery_address = (
            db.query(Address)
            .filter(
                Address.id == shipment_data.delivery_address_id,
                Address.user_id == shipment_data.recipient_id,
                Address.is_deleted == False,
            )
            .first()
        )
        if not delivery_address:
            raise HTTPException(status_code=400, detail="Invalid delivery address")

        # 7. Validate package
        package = (
            db.query(Package)
            .filter(Package.id == shipment_data.package_id, Package.is_deleted == False)
            .first()
        )
        if not package:
            raise HTTPException(status_code=400, detail="Invalid package")
        if user_obj.user_type != "super_admin" and package.user_id != user_obj.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to use this package"
            )

        # 8. Replace fields
        for field, value in shipment_data.dict().items():
            setattr(shipment, field, value)

        db.commit()
        db.refresh(shipment)

        # 9. Return validated response
        return FetchShipment.model_validate(shipment)


# ========================= PACKAGE SERVICE =========================


class PackageService:
    async def create_package(request, package_data: CreatePackage, db: Session):

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

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
            user_id=user_obj.id,
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
        request,
        db: Session,
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type == "super_admin":
            query = db.query(Package).filter(Package.is_deleted == False)
        else:
            query = db.query(Package).filter(
                Package.user_id == user_id, Package.is_deleted == False
            )

        if package_type:
            try:
                query = query.filter(Package.package_type == PackageType(package_type))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid package_type")

        if currency_id:
            query = query.filter(Package.currency_id == currency_id)

        if is_negotiable is not None:
            query = query.filter(Package.is_negotiable == is_negotiable)

        if user_id:
            query = query.filter(Package.user_id == user_id)

        total = query.count()
        results = query.offset((page - 1) * limit).limit(limit).all()

        return {"page": page, "limit": limit, "total": total, "results": results}

    # async def get_package_by_id(package_id: int, db: Session):
    #     package = db.query(Package).filter(Package.id == package_id).first()

    #     if not package:
    #         raise HTTPException(status_code=404, detail="Package not found")

    #     if package.is_deleted:
    #         raise HTTPException(status_code=403, detail="Package has been deleted")

    #     return package

    @staticmethod
    async def update_package(
        request, package_id: int, payload: UpdatePackage, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        package = (
            db.query(Package)
            .filter(Package.id == package_id, Package.is_deleted == False)
            .first()
        )
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        # Optional: check if user owns the package (if model supports ownership)
        if package.user_id != user.id and user.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Not authorized to update this package"
            )

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(package, field, value)

        db.commit()
        db.refresh(package)
        return FetchPackage.model_validate(package)

    @staticmethod
    async def replace_package(
        request, package_id: int, package_data: ReplacePackage, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_deleted:
            raise HTTPException(status_code=403, detail="Package has been deleted")

        # Ownership check (adjust field name as per your model)
        if (
            getattr(package, "user_id", None) != user.id
            and user.user_type != "super_admin"
        ):
            raise HTTPException(
                status_code=403, detail="You are not authorized to modify this package"
            )

        for field, value in package_data.dict().items():
            setattr(package, field, value)

        db.commit()
        db.refresh(package)
        return FetchPackage.model_validate(package)


# ========================= STATUS TRACKER SERVICE =========================


class StatusTrackerService:
    @staticmethod
    async def create_status_tracker(
        request, request_data: CreateStatusTracker, db: Session
    ):
        # Get signed-in user
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate shipment existence
        shipment = (
            db.query(Shipment)
            .filter_by(id=request_data.shipment_id, is_deleted=False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Validate user is allowed to access this shipment
        if user_obj.user_type != "super_admin" and shipment.sender_id != user_obj.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this shipment"
            )

        # Check if a status tracker already exists for this shipment
        existing_status = db.query(StatusTracker).filter(
            StatusTracker.shipment_id == request_data.shipment_id,
            Payment.is_deleted == False
        ).first()

        if existing_status:
            raise HTTPException(
                status_code=400, detail="Shipment already exists"
            )

        # Create the tracker
        tracker = StatusTracker(
            shipment_id=request_data.shipment_id,
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
    async def get_status(
        request,
        db: Session,
        shipment_id: Optional[int] = None,
        package_id: Optional[int] = None,
        status: Optional[ShipmentStatus] = None,
        is_delivered: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        # Get user info from request
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Start base query
        query = (
            db.query(StatusTracker)
            .filter(StatusTracker.is_deleted == False)
            .options(
                joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
            )
        )

        # Filter based on user type
        if user_obj.user_type != "super_admin":
            # Limit to only shipments created by the user
            query = query.join(StatusTracker.shipment).filter(
                Shipment.sender_id == user_obj.id
            )

        # Optional filters
        if shipment_id:
            query = query.filter(StatusTracker.shipment_id == shipment_id)

        if package_id:
            query = query.filter(StatusTracker.package_id == package_id)

        if status:
            query = query.filter(StatusTracker.status == status)

        if is_delivered is not None:
            query = query.filter(StatusTracker.is_delivered == is_delivered)

        # Pagination
        total = query.count()
        status_records = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchStatus.model_validate(s) for s in status_records],
        }

    # @staticmethod
    # async def get_status_by_id(status_id: int, db: Session):
    #     status_record = (
    #         db.query(StatusTracker)
    #         .options(
    #             joinedload(StatusTracker.shipment), joinedload(StatusTracker.package)
    #         )
    #         .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
    #         .first()
    #     )

    #     if not status_record:
    #         raise HTTPException(status_code=404, detail="Status record not found")

    #     return FetchStatus.model_validate(status_record)

    async def update_status_tracker(
        request,
        status_id: int,
        status_data: UpdateStatusTracker,
        db: Session,
    ):
        # Get the current user
        user_id = request.state.user.get("sub")
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the status tracker
        status = (
            db.query(StatusTracker)
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

        if not status:
            raise HTTPException(status_code=404, detail="Status record not found.")

        # Validate permission: only super_admin or shipment sender can update
        if user_obj.user_type != "super_admin":
            if not status.shipment or status.shipment.sender_id != user_obj.id:
                raise HTTPException(
                    status_code=403, detail="Not authorized to update this status"
                )

        # Update fields if provided
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

    async def replace_status_tracker(
        request, status_id: int, new_data: ReplaceStatus, db: Session
    ):
        # Get user from token
        user_id = request.state.user.get("sub")
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Get existing status
        status = (
            db.query(StatusTracker)
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

        if not status:
            raise HTTPException(status_code=404, detail="Status record not found")

        # Validate new shipment exists
        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == new_data.shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=400, detail="Shipment not found")

        # Only allow if user is super_admin or shipment owner
        if user_obj.user_type != "super_admin" and shipment.sender_id != user_obj.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this status"
            )

        # Replace all fields
        status.shipment_id = new_data.shipment_id
        status.package_id = new_data.package_id
        status.status = new_data.status
        status.current_location = new_data.current_location
        status.is_delivered = new_data.is_delivered
        status.is_deleted = new_data.is_deleted

        try:
            db.commit()
            db.refresh(status)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Failed to replace status: {str(e)}"
            )

        return status


# ============================PAYMENT SERVICE======================


class PaymentService:
    @staticmethod
    async def create_payment(request, payment_data : CreatePayment, db: Session):
        user_id = request.state.user.get("sub", None)
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate shipment
        shipment = db.query(Shipment).filter(Shipment.id==payment_data.shipment_id).first()
        
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        existing_payment = db.query(Payment).filter(
            Payment.shipment_id == payment_data.shipment_id,
            Payment.payment_status == PaymentStatus.PENDING.value,
            Payment.is_deleted == False
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=400, detail="Payment already pending for this shipment"
            )
        
        existing_payment = db.query(Payment).filter(
            Payment.shipment_id == payment_data.shipment_id,
            Payment.payment_status == PaymentStatus.COMPLETED.value,
            Payment.is_deleted == False
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=400, detail="Payment already completed for this shipment"
            )

        payment = Payment(
            shipment_id=payment_data.shipment_id,
            package_id=shipment.package_id,
            payment_method=payment_data.payment_method,
            payment_status=payment_data.payment_status,
            payment_date=payment_data.payment_date,
        )



        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    async def get_payments(
        request,
        db: Session,
        shipment_id: Optional[int] = None,
        package_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        payment_status: Optional[str] = None,
        payment_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 10,
    ):
        # Get authenticated user
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        query = (
            db.query(Payment)
            .filter(Payment.is_deleted == False)
            .options(joinedload(Payment.shipment), joinedload(Payment.package))
        )

        # If not super_admin, restrict to user's shipments only
        if user_obj.user_type != "super_admin":
            query = query.join(Payment.shipment).filter(
                Shipment.sender_id == user_obj.id
            )

        # Optional filters
        if shipment_id is not None:
            query = query.filter(Payment.shipment_id == shipment_id)

        if package_id is not None:
            query = query.filter(Payment.package_id == package_id)

        if payment_method:
            try:
                query = query.filter(
                    Payment.payment_method == PaymentMethod(payment_method)
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payment method")

        if payment_status:
            try:
                query = query.filter(
                    Payment.payment_status == PaymentStatus(payment_status)
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payment status")

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

    # @staticmethod
    # async def get_payment_by_id(payment_id: int, db: Session):
    #     payment = (
    #         db.query(Payment)
    #         .options(joinedload(Payment.shipment), joinedload(Payment.package))
    #         .filter(Payment.id == payment_id, Payment.is_deleted == False)
    #         .first()
    #     )

    #     if not payment:
    #         raise HTTPException(status_code=404, detail="Payment not found")

    #     return FetchPayment.model_validate(payment)

    @staticmethod
    async def update_payment(
        request, payment_id: int, new_data: UpdatePayment, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # If not admin, ensure ownership
        if user.user_type != "super_admin":
            if not payment.shipment or payment.shipment.sender_id != user.id:
                raise HTTPException(
                    status_code=403, detail="Not authorized to update this payment"
                )

        # Update fields
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
    async def replace_payment(
        request, payment_id: int, new_data: ReplacePayment, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id, Payment.is_deleted == False)
            .first()
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Validate shipment
        shipment = (
            db.query(Shipment).filter(Shipment.id == new_data.shipment_id).first()
        )
        if not shipment:
            raise HTTPException(status_code=400, detail="Shipment not found")

        # If not admin, verify shipment ownership
        if user.user_type != "super_admin" and shipment.sender_id != user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to replace this payment"
            )

        # Replace fields
        payment.shipment_id = new_data.shipment_id
        payment.package_id = new_data.package_id
        payment.payment_method = new_data.payment_method
        payment.payment_status = new_data.payment_status
        payment.payment_date = new_data.payment_date
        payment.is_deleted = new_data.is_deleted

        db.commit()
        db.refresh(payment)
        return payment
