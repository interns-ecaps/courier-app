from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import desc, or_
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.status import ShipmentStatus, StatusTracker
from shipment.api.v1.models.shipment import Shipment
from razorpay import Client
import json
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

        # Validate assigned supplier (courier_id is still used for assignment, but user_type is always 'supplier')
        assigned_supplier = (
            db.query(User)
            .filter(
                User.id == shipment_data.courier_id,
                User.is_deleted == False,
                User.is_active == True,
                User.user_type == "supplier",
            )
            .first()
        )
        if not assigned_supplier:
            raise HTTPException(
                status_code=400, detail="Assigned supplier not found or inactive"
            )

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
            delivery_address_text=shipment_data.delivery_address_text,
            recipient_name=shipment_data.recipient_name,
            recipient_phone=shipment_data.recipient_phone,
            recipient_email=shipment_data.recipient_email,
            courier_id=shipment_data.courier_id,
            shipment_type=shipment_data.shipment_type,
            package_id=shipment_data.package_id,
            pickup_date=shipment_data.pickup_date,
            special_instructions=shipment_data.special_instructions,
            insurance_required=shipment_data.insurance_required,
            signature_required=shipment_data.signature_required,
        )

        db.add(new_shipment)
        db.commit()
        # Always create a StatusTracker entry for PENDING
        new_status_tracker = StatusTracker(
            shipment_id=new_shipment.id,
            status=ShipmentStatus.PENDING,
            package_id=new_shipment.package_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_status_tracker)
        db.commit()
        db.refresh(new_shipment)
        return new_shipment

    @staticmethod
    async def get_shipments(
        request,
        db: Session,
        shipment_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        user_id: Optional[int] = None,  # retained for backward compatibility
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        courier_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        shipment_type: Optional[str] = None,
        status_type: Optional[str] = None,
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

        # Start with all statuses (used to get shipment IDs)
        statuses_obj = db.query(StatusTracker).all()

        # Apply status filter if passed
        if status_type:
            statuses_obj = [
                s for s in statuses_obj if s.status.lower() == status_type.lower()
            ]

        shipment_ids = {s.shipment_id for s in statuses_obj}

        # Build base query with shipment_ids found from statuses
        query = db.query(Shipment).filter(
            Shipment.id.in_(shipment_ids), Shipment.is_deleted == False
        )

        # Role-based filters
        if user_obj.user_type == "super_admin":
            pass  # See all shipments
        elif user_obj.user_type == "supplier":
            query = query.filter(Shipment.courier_id == user_obj.id)
        elif user_obj.user_type == "importer_exporter":
            query = query.filter(Shipment.sender_id == user_obj.id)
        else:
            # Default: no shipments
            query = query.filter(False)

        # Optional filters
        if shipment_id is not None:
            query = query.filter(Shipment.id == shipment_id)
        if sender_id is not None:
            query = query.filter(Shipment.sender_id == sender_id)
        if package_type is not None:
            query = query.filter(Shipment.package_type == package_type)
        if currency_id is not None:
            query = query.filter(Shipment.currency_id == currency_id)
        if courier_id is not None:
            query = query.filter(Shipment.courier_id == courier_id)
        if is_negotiable is not None:
            query = query.filter(Shipment.is_negotiable == is_negotiable)
        if shipment_type is not None:
            query = query.filter(Shipment.shipment_type == shipment_type)
        if pickup_from is not None:
            query = query.filter(Shipment.pickup_date >= pickup_from)
        if pickup_to is not None:
            query = query.filter(Shipment.pickup_date <= pickup_to)

        # Pagination
        offset = (page - 1) * limit
        shipment_objs = (
            query.order_by(Shipment.created_at.desc()).offset(offset).limit(limit).all()
        )

        results = []
        for shipment in shipment_objs:
            # Get latest status from StatusTracker (if multiple)
            latest_status = (
                db.query(StatusTracker)
                .filter(StatusTracker.shipment_id == shipment.id)
                .order_by(StatusTracker.id.desc())
                .first()
            )

            shipment_data = {
                "id": shipment.id,
                "tracking_number": shipment.tracking_number,
                "sender_id": shipment.sender_id,
                "sender_name": shipment.sender_name,
                "sender_phone": shipment.sender_phone,
                "sender_email": shipment.sender_email,
                "recipient_name": shipment.recipient_name,
                "recipient_phone": shipment.recipient_phone,
                "recipient_email": shipment.recipient_email,
                # Show supplier name instead of courier_id
                "supplier_name": None,
                "pickup_address_id": shipment.pickup_address_id,
                "delivery_address_text": shipment.delivery_address_text,
                "status_type": latest_status.status if latest_status else "PENDING",
                "pickup_date": shipment.pickup_date,
                "delivery_date": shipment.delivery_date,
                "estimated_delivery": shipment.estimated_delivery,
                "special_instructions": shipment.special_instructions,
                "insurance_required": shipment.insurance_required,
                "signature_required": shipment.signature_required,
                "package_id": shipment.package_id,
                "is_deleted": shipment.is_deleted,
                "created_at": shipment.created_at,
                "updated_at": shipment.updated_at,
                "status_id": latest_status.id if latest_status else None,
            }
            # Lookup supplier name if assigned
            if shipment.courier_id:
                supplier = db.query(User).filter(User.id == shipment.courier_id).first()
                if supplier:
                    shipment_data["supplier_name"] = (
                        f"{supplier.first_name} {supplier.last_name}"
                    )
            
            # Add payment status
            payment = db.query(Payment).filter(
                Payment.shipment_id == shipment.id, 
                Payment.is_deleted == False
            ).first()
            shipment_data["payment_status"] = payment.payment_status.value if payment else None
            
            results.append(shipment_data)

        total = query.count()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": results,
        }

    @staticmethod
    async def get_shipment_by_id(request, shipment_id: int, db: Session):
        shipment = (
            db.query(Shipment)
            .options(joinedload(Shipment.packages))
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )

        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=403, detail="User not found.")

        # Only the creator (importer/exporter), assigned supplier, or super admin can view
        if not (
            user_obj.user_type == "super_admin"
            or (
                user_obj.user_type == "importer_exporter"
                and shipment.sender_id == user_obj.id
            )
            or (user_obj.user_type == "supplier" and shipment.courier_id == user_obj.id)
        ):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this shipment.",
            )

        # Fetch all status tracker entries for this shipment
        status_priority = {"PENDING": 1, "ACCEPTED": 2, "IN_TRANSIT": 3, "DELIVERED": 4}
        status_history = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == shipment_id)
            .order_by(StatusTracker.created_at.desc())
            .all()
        )
        # Convert to dicts or use FetchStatus schema if needed
        status_history_data = [
            {
                "status": (
                    s.status.value if hasattr(s.status, "value") else str(s.status)
                ),
                "created_at": s.created_at,
                "priority": status_priority.get(
                    s.status.value if hasattr(s.status, "value") else str(s.status), 0
                ),
            }
            for s in status_history
        ]
        status_history_data = sorted(status_history_data, key=lambda x: x["priority"])
        # Set latest status as status_type
        latest_status_obj = (
            max(
                status_history,
                key=lambda s: status_priority.get(
                    s.status.value if hasattr(s.status, "value") else str(s.status), 0
                ),
            )
            if status_history
            else None
        )
        status_type = latest_status_obj.status.value if latest_status_obj else None
        
        # Ensure we have a status tracker and get its ID
        if not latest_status_obj:
            print(f"[DEBUG] No status tracker found for shipment {shipment_id}, creating one...")
            status_id = ensure_shipment_has_status_tracker(shipment_id, db)
            if status_id:
                latest_status_obj = db.query(StatusTracker).filter(StatusTracker.id == status_id).first()
                status_type = latest_status_obj.status.value if latest_status_obj else "PENDING"
            else:
                print(f"[DEBUG] Failed to create status tracker for shipment {shipment_id}")
                status_type = "PENDING"
        else:
            status_id = latest_status_obj.id
        
        # Fetch related details
        # Package details
        package = db.query(Package).filter(Package.id == shipment.package_id).first()
        # Do NOT block viewing if final_cost is missing or zero
        if package:
            package_label = f"{package.package_type.value.replace('_', ' ').title()} ({package.weight}kg, {package.length}x{package.width}x{package.height}cm)"
            package_details = {
                "id": package.id,
                "label": package_label,
                "type": package.package_type.value,
                "weight": float(package.weight),
                "length": float(package.length),
                "width": float(package.width),
                "height": float(package.height),
                "is_negotiable": package.is_negotiable,
                "estimated_cost": (
                    float(package.estimated_cost) if package.estimated_cost else None
                ),
                "final_cost": float(package.final_cost) if package.final_cost else 0,
                "currency": package.currency.currency if package.currency else None,
            }
        else:
            package_details = None

        # Supplier (sender) details
        sender = db.query(User).filter(User.id == shipment.sender_id).first()
        sender_name = (
            f"{sender.first_name} {sender.last_name}"
            if sender
            else shipment.sender_name
        )

        # Courier details
        courier = (
            db.query(User).filter(User.id == shipment.courier_id).first()
            if shipment.courier_id
            else None
        )
        courier_name = f"{courier.first_name} {courier.last_name}" if courier else None

        # Pickup address label
        pickup_address = (
            db.query(Address).filter(Address.id == shipment.pickup_address_id).first()
        )
        pickup_address_label = (
            pickup_address.label if pickup_address and pickup_address.label else None
        )

        # Build response
        shipment_data = FetchShipment.model_validate(shipment).dict()
        shipment_data["delivery_address_text"] = shipment.delivery_address_text
        shipment_data["package"] = package_details
        shipment_data["package_label"] = (
            package_details["label"] if package_details else None
        )
        shipment_data["sender_name"] = sender_name
        shipment_data["courier_name"] = courier_name
        shipment_data["pickup_address_label"] = pickup_address_label
        # Remove package_id from response
        if "package_id" in shipment_data:
            del shipment_data["package_id"]
        # Add status info
        shipment_data["status_history"] = status_history_data
        shipment_data["status_type"] = status_type
        shipment_data["status_id"] = latest_status_obj.id if latest_status_obj else None
        
        # Add payment status
        payment = db.query(Payment).filter(
            Payment.shipment_id == shipment_id, 
            Payment.is_deleted == False
        ).first()
        shipment_data["payment_status"] = payment.payment_status.value if payment else None
        
        return shipment_data

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

        # Fetch latest status for the shipment
        latest_status = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == shipment_id)
            .order_by(StatusTracker.id.desc())
            .first()
        )
        final_statuses = {"DELIVERED", "CANCELLED", "REJECTED"}
        current_status = (
            latest_status.status.value if latest_status and hasattr(latest_status.status, "value") else str(latest_status.status) if latest_status else None
        )

        # Only allow update if not in a final state
        if current_status and current_status.upper() in final_statuses:
            raise HTTPException(status_code=403, detail=f"Cannot update shipment in final state: {current_status}")

        # Permission: allow assigned supplier (courier), or super_admin
        is_supplier = user_obj.user_type == "supplier" and shipment.courier_id == user_obj.id
        is_super_admin = user_obj.user_type == "super_admin"
        if not (is_supplier or is_super_admin):
            raise HTTPException(
                status_code=403,
                detail="Only the assigned supplier or a super_admin can update estimated_delivery for this shipment."
            )

        # Additional restriction: Only allow update if status is IN_TRANSIT and payment is COMPLETED
        if not (current_status and current_status.upper() == "IN_TRANSIT"):
            raise HTTPException(status_code=403, detail="ETA can only be updated when shipment status is IN_TRANSIT.")
        payment = db.query(Payment).filter(Payment.shipment_id == shipment_id, Payment.is_deleted == False).order_by(Payment.id.desc()).first()
        payment_completed = payment and ((payment.payment_status.value if hasattr(payment.payment_status, "value") else str(payment.payment_status)) == "COMPLETED")
        if not payment_completed:
            raise HTTPException(status_code=403, detail="ETA can only be updated after payment is COMPLETED.")

        # Only allow updating estimated_delivery (other fields ignored if present)
        update_fields = shipment_data.dict(exclude_unset=True)
        if not update_fields or "estimated_delivery" not in update_fields:
            raise HTTPException(status_code=400, detail="estimated_delivery field is required.")
        shipment.estimated_delivery = update_fields["estimated_delivery"]

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

    @staticmethod
    async def cancel_shipment(request, shipment_id: int, db: Session):
        """
        Only importer_exporter can cancel a shipment, and only if status is 'pending' or 'in_transit'.
        """
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj or user_obj.user_type != "importer_exporter":
            raise HTTPException(
                status_code=403, detail="Only importer/exporter can cancel shipments."
            )

        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Find the latest status tracker for this shipment
        status_tracker = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == shipment_id)
            .order_by(StatusTracker.created_at.desc())
            .first()
        )
        if not status_tracker:
            raise HTTPException(
                status_code=404, detail="Status tracker not found for shipment"
            )

        if status_tracker.status.value.lower() not in [
            "pending",
            "in_transit",
            "accepted",
        ]:
            raise HTTPException(
                status_code=400,
                detail="Can only cancel shipments that are pending, in transit, or accepted (not delivered).",
            )

        status_tracker.status = "CANCELLED"
        db.commit()
        db.refresh(shipment)

        # When cancelling, create a new StatusTracker entry for CANCELLED
        new_status_tracker = StatusTracker(
            shipment_id=shipment.id,
            status="CANCELLED",
            package_id=shipment.package_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_status_tracker)
        db.commit()
        return {"detail": "Shipment cancelled", "status": status_tracker.status}

    @staticmethod
    async def accept_reject_shipment(
        request, shipment_id: int, action: str, db: Session
    ):
        """
        Accepts or rejects a shipment by updating its status.
        - Only supplier/courier can accept/reject (if status is 'pending' or 'in_transit').
        - Only allow reject if payment is NOT completed.
        - Only importer_exporter can cancel (handled in cancel_shipment).
        Args:
            request: FastAPI request object (for user info)
            shipment_id: ID of the shipment to update
            action: 'accept' or 'reject'
            db: SQLAlchemy session
        Returns:
            Updated shipment object
        """
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=403, detail="User not found.")

        shipment = (
            db.query(Shipment)
            .filter(Shipment.id == shipment_id, Shipment.is_deleted == False)
            .first()
        )
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Find the latest status tracker for this shipment
        status_tracker = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == shipment_id)
            .order_by(StatusTracker.created_at.desc())
            .first()
        )
        if not status_tracker:
            raise HTTPException(
                status_code=404, detail="Status tracker not found for shipment"
            )

        # Only supplier can accept/reject
        if user_obj.user_type != "supplier":
            raise HTTPException(
                status_code=403, detail="Only suppliers can accept or reject shipments."
            )

        # Only allow if status is pending or in_transit
        # if status_tracker.status.value.lower() not in ["pending", "in_transit"]:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Can only accept or reject shipments that are pending or in transit.",
        #     )

        # Get payment for this shipment
        payment = (
            db.query(Payment)
            .filter(Payment.shipment_id == shipment_id, Payment.is_deleted == False)
            .first()
        )
        print(f"DEBUG: Payment found: {payment is not None}")
        if payment:
            print(f"DEBUG: Payment ID: {payment.id}")
            print(f"DEBUG: Payment status: {payment.payment_status}")
            print(f"DEBUG: Expected status: {PaymentStatus.COMPLETED.value}")
        payment_completed = (
            payment and payment.payment_status == PaymentStatus.COMPLETED
        )

        # Check current status to determine payment requirements
        current_status = status_tracker.status.value.upper()
        print(f"DEBUG: Current status: {current_status}, Action: {action}, Payment completed: {payment_completed}")
        
        # Enforce sequential status transitions
        if action.lower() == "accept" or action.lower() == "accepted":
            if current_status != "PENDING":
                raise HTTPException(status_code=400, detail="Can only accept a shipment from PENDING status.")
            new_status = "ACCEPTED"
        elif action.lower() == "in_transit":
            if current_status != "ACCEPTED":
                raise HTTPException(status_code=400, detail="Can only mark as IN_TRANSIT from ACCEPTED status.")
            if not payment_completed:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot move shipment to IN_TRANSIT. Payment must be completed first.",
                )
            new_status = "IN_TRANSIT"
        elif action.lower() == "delivered":
            if current_status != "IN_TRANSIT":
                raise HTTPException(status_code=400, detail="Can only mark as DELIVERED from IN_TRANSIT status.")
            if not payment_completed:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot mark shipment as DELIVERED. Payment must be completed first.",
                )
            new_status = "DELIVERED"
        elif action.lower() == "reject" or action.lower() == "rejected":
            new_status = "REJECTED"
        else:
            raise HTTPException(
                status_code=400, detail="Invalid action. Must be 'accept', 'reject', 'in_transit', or 'delivered'."
            )
        # Instead of only updating the status, always create a new StatusTracker entry
        new_status_tracker = StatusTracker(
            shipment_id=shipment.id,
            status=new_status,
            package_id=status_tracker.package_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_status_tracker)
        # Update main shipment status
        # shipment.status = new_status  # <-- keep main shipment status in sync
        db.commit()
        db.refresh(shipment)
        return shipment


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
            final_cost=package_data.final_cost,  # <-- set from request
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

    async def get_package_by_id(request, package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_deleted:
            raise HTTPException(status_code=403, detail="Package has been deleted")

        return package

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
        print("enter ejre")
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
        existing_status = (
            db.query(StatusTracker)
            .filter(
                StatusTracker.shipment_id == request_data.shipment_id,
                Payment.is_deleted == False,
            )
            .first()
        )

        if existing_status:
            raise HTTPException(status_code=400, detail="Shipment already exists")

        # Create the tracker
        tracker = StatusTracker(
            shipment_id=request_data.shipment_id,
            package_id=shipment.package_id,
            status=ShipmentStatus.PENDING,
            current_location=None,
            is_delivered=False,
        )
        print(tracker, "::tracker")

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

    @staticmethod
    async def get_status_by_id(request, status_id: int, db: Session):
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

    @staticmethod
    async def update_status_tracker(
        request,
        status_id: int,
        status_data: UpdateStatusTracker,
        db: Session,
    ):
        print(f"[DEBUG] === STATUS UPDATE REQUEST ===")
        print(f"[DEBUG] Status ID: {status_id}")
        print(f"[DEBUG] Payload: {status_data.dict()}")
        
        # Get the current user
        user_id = request.state.user.get("sub")
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user_obj:
            print(f"[DEBUG] User not found for ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        print(f"[DEBUG] User ID: {user_id}, User Type: {user_obj.user_type}")

        # Fetch the status tracker with shipment relationship loaded
        status = (
            db.query(StatusTracker)
            .options(joinedload(StatusTracker.shipment))
            .filter(StatusTracker.id == status_id, StatusTracker.is_deleted == False)
            .first()
        )

        if not status:
            print(f"[DEBUG] Status tracker not found for ID: {status_id}")
            raise HTTPException(status_code=404, detail="Status record not found.")

        print(f"[DEBUG] Found status tracker - Shipment ID: {status.shipment_id}, Current Status: {status.status}")
        
        # Validate permission: super_admin, shipment sender, or assigned supplier can update
        if user_obj.user_type != "super_admin":
            shipment = status.shipment
            if not shipment:
                print(f"[DEBUG] No shipment found for status {status_id}, trying direct fetch...")
                # Try to fetch shipment directly
                shipment = db.query(Shipment).filter(Shipment.id == status.shipment_id).first()
                if not shipment:
                    print(f"[DEBUG] Shipment not found for ID: {status.shipment_id}")
                    raise HTTPException(status_code=404, detail="Shipment not found for this status")
            
            print(f"[DEBUG] Shipment found - Sender ID: {shipment.sender_id}, Courier ID: {shipment.courier_id}")
            
            # Check if user is the sender (importer/exporter)
            is_sender = shipment.sender_id == user_obj.id
            # Check if user is the assigned supplier (courier)
            is_assigned_supplier = shipment.courier_id == user_obj.id and user_obj.user_type == "supplier"
            
            print(f"[DEBUG] Permission check - Is sender: {is_sender}, Is assigned supplier: {is_assigned_supplier}")
            
            if not (is_sender or is_assigned_supplier):
                print(f"[DEBUG] Permission denied for user {user_id} (type: {user_obj.user_type})")
                print(f"[DEBUG] Shipment sender: {shipment.sender_id}, Courier: {shipment.courier_id}")
                raise HTTPException(
                    status_code=403, detail="Not authorized to update this status"
                )

        print(f"[DEBUG] Permission granted, proceeding with update...")

        # Payment enforcement logic for suppliers
        if user_obj.user_type == "supplier" and status_data.status is not None:
            # Get payment for this shipment
            payment = (
                db.query(Payment)
                .filter(Payment.shipment_id == status.shipment_id, Payment.is_deleted == False)
                .first()
            )
            payment_completed = (
                payment and payment.payment_status == PaymentStatus.COMPLETED
            )
            
            print(f"[DEBUG] Payment check - Payment exists: {payment is not None}, Payment completed: {payment_completed}")
            
            # Allow initial acceptance without payment
            if status_data.status.value == "ACCEPTED" and status.status.value == "PENDING":
                print(f"[DEBUG] Allowing initial acceptance from PENDING to ACCEPTED without payment requirement")
            # Require payment for advanced status changes
            elif status_data.status.value in ["IN_TRANSIT", "DELIVERED"] and not payment_completed:
                print(f"[DEBUG] Payment required for status change to {status_data.status.value}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot change status to {status_data.status.value}. Payment must be completed first."
                )
            # Allow rejection without payment
            elif status_data.status.value == "REJECTED":
                print(f"[DEBUG] Allowing rejection without payment requirement")
            # For other status changes, check payment
            elif status_data.status.value != "PENDING" and not payment_completed:
                print(f"[DEBUG] Payment required for status change to {status_data.status.value}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot change status to {status_data.status.value}. Payment must be completed first."
                )

        # Enforce sequential status transitions and prevent duplicates
        requested_status = status_data.status.value if hasattr(status_data.status, "value") else str(status_data.status)
        
        # Get the latest status for this shipment (not the status of the specific row being updated)
        latest_status = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == status.shipment_id)
            .order_by(StatusTracker.created_at.desc())
            .first()
        )
        current_status = latest_status.status.value if latest_status and hasattr(latest_status.status, "value") else str(latest_status.status) if latest_status else "PENDING"
        
        print(f"[DEBUG] Latest status: {current_status}, Requested status: {requested_status}")
        
        if requested_status == current_status:
            raise HTTPException(status_code=400, detail="Cannot set the same status twice in a row.")
        if requested_status == "ACCEPTED" and current_status != "PENDING":
            raise HTTPException(status_code=400, detail="Can only accept a shipment from PENDING status.")
        if requested_status == "IN_TRANSIT" and current_status != "ACCEPTED":
            raise HTTPException(status_code=400, detail="Can only mark as IN_TRANSIT from ACCEPTED status.")
        if requested_status == "DELIVERED" and current_status != "IN_TRANSIT":
            raise HTTPException(status_code=400, detail="Can only mark as DELIVERED from IN_TRANSIT status.")
        # Allow REJECTED from any status
        # Update fields if provided (but NOT the status field)
        if status_data.current_location is not None:
            print(f"[DEBUG] Updating location to: {status_data.current_location}")
            status.current_location = status_data.current_location

        if status_data.is_delivered is not None:
            print(f"[DEBUG] Updating is_delivered to: {status_data.is_delivered}")
            status.is_delivered = status_data.is_delivered

        if status_data.is_deleted is not None:
            print(f"[DEBUG] Updating is_deleted to: {status_data.is_deleted}")
            status.is_deleted = status_data.is_deleted

        # Create a new StatusTracker entry for the status change
        if status_data.status is not None:
            print(f"[DEBUG] Creating new StatusTracker entry for status: {status_data.status}")
            new_status_tracker = StatusTracker(
                shipment_id=status.shipment_id,
                status=status_data.status,
                package_id=status.package_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(new_status_tracker)

        try:
            db.commit()
            db.refresh(status)
            print(f"[DEBUG] Status update successful")
        except Exception as e:
            db.rollback()
            print(f"[DEBUG] Database error during update: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error while updating status: {str(e)}"
            )

        return status

    @staticmethod
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
            .options(joinedload(StatusTracker.shipment))
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

        # Validate permission: super_admin, shipment sender, or assigned supplier can update
        if user_obj.user_type != "super_admin":
            # Check if user is the sender (importer/exporter)
            is_sender = shipment.sender_id == user_obj.id
            # Check if user is the assigned supplier (courier)
            is_assigned_supplier = shipment.courier_id == user_obj.id and user_obj.user_type == "supplier"
            
            if not (is_sender or is_assigned_supplier):
                raise HTTPException(
                    status_code=403, detail="Not authorized to update this status"
                )

        # Enforce sequential status transitions and prevent duplicates
        requested_status = new_data.status.value if hasattr(new_data.status, "value") else str(new_data.status)
        
        # Get the latest status for this shipment (not the status of the specific row being updated)
        latest_status = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == status.shipment_id)
            .order_by(StatusTracker.created_at.desc())
            .first()
        )
        current_status = latest_status.status.value if latest_status and hasattr(latest_status.status, "value") else str(latest_status.status) if latest_status else "PENDING"
        
        print(f"[DEBUG] Latest status: {current_status}, Requested status: {requested_status}")
        
        if requested_status == current_status:
            raise HTTPException(status_code=400, detail="Cannot set the same status twice in a row.")
        if requested_status == "ACCEPTED" and current_status != "PENDING":
            raise HTTPException(status_code=400, detail="Can only accept a shipment from PENDING status.")
        if requested_status == "IN_TRANSIT" and current_status != "ACCEPTED":
            raise HTTPException(status_code=400, detail="Can only mark as IN_TRANSIT from ACCEPTED status.")
        if requested_status == "DELIVERED" and current_status != "IN_TRANSIT":
            raise HTTPException(status_code=400, detail="Can only mark as DELIVERED from IN_TRANSIT status.")
        # Allow REJECTED from any status
        # Create new StatusTracker entry for the status change
        new_status_tracker = StatusTracker(
            shipment_id=status.shipment_id,
            status=new_data.status,
            package_id=status.package_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_status_tracker)
        db.commit()

        # Update fields if provided
        original_status = status.status
        if new_data.status is not None:
            print(f"[DEBUG] Updating status from {original_status} to {new_data.status}")
            status.status = new_data.status

        if new_data.current_location is not None:
            print(f"[DEBUG] Updating location to: {new_data.current_location}")
            status.current_location = new_data.current_location

        if new_data.is_delivered is not None:
            print(f"[DEBUG] Updating is_delivered to: {new_data.is_delivered}")
            status.is_delivered = new_data.is_delivered

        if new_data.is_deleted is not None:
            print(f"[DEBUG] Updating is_deleted to: {new_data.is_deleted}")
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
    async def create_payment(request, payment_data: CreatePayment, db: Session):
        user_id = request.state.user.get("sub", None)
        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate shipment
        shipment = (
            db.query(Shipment).filter(Shipment.id == payment_data.shipment_id).first()
        )

        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # ENFORCE: Only allow payment if latest status is ACCEPTED
        latest_status = (
            db.query(StatusTracker)
            .filter(StatusTracker.shipment_id == payment_data.shipment_id)
            .order_by(StatusTracker.id.desc())
            .first()
        )
        if not latest_status or str(latest_status.status) != "ACCEPTED":
            raise HTTPException(status_code=400, detail="Payment can only be made after supplier accepts the shipment.")

        # Store Razorpay order ID if provided
        razorpay_order_id = getattr(payment_data, 'razorpay_order_id', None)

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.shipment_id == payment_data.shipment_id,
                Payment.payment_status == PaymentStatus.PENDING.value,
                Payment.is_deleted == False,
            )
            .first()
        )

        if existing_payment:
            raise HTTPException(
                status_code=400, detail="Payment already pending for this shipment"
            )

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.shipment_id == payment_data.shipment_id,
                Payment.payment_status == PaymentStatus.COMPLETED.value,
                Payment.is_deleted == False,
            )
            .first()
        )

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
            razorpay_order_id=razorpay_order_id
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

    @staticmethod
    async def get_payment_by_id(request, payment_id: int, db: Session):
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


def ensure_shipment_has_status_tracker(shipment_id: int, db: Session):
    """
    Ensure a shipment has a status tracker. If not, create one.
    Returns the status tracker ID.
    """
    # Check if status tracker exists
    existing_status = (
        db.query(StatusTracker)
        .filter(StatusTracker.shipment_id == shipment_id, StatusTracker.is_deleted == False)
        .first()
    )
    
    if existing_status:
        print(f"[DEBUG] Status tracker already exists for shipment {shipment_id}: {existing_status.id}")
        return existing_status.id
    
    # Get shipment to get package_id
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        print(f"[DEBUG] Shipment {shipment_id} not found")
        return None
    
    # Create new status tracker
    new_status = StatusTracker(
        shipment_id=shipment_id,
        package_id=shipment.package_id,
        status=ShipmentStatus.PENDING,
        current_location=None,
        is_delivered=False,
    )
    
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    
    print(f"[DEBUG] Created new status tracker {new_status.id} for shipment {shipment_id}")
    return new_status.id


def create_missing_status_trackers(db: Session):
    """Utility: Create StatusTracker for all shipments that do not have one."""
    from shipment.api.v1.models.shipment import Shipment
    from shipment.api.v1.models.status import StatusTracker, ShipmentStatus
    shipments = db.query(Shipment).filter(Shipment.is_deleted == False).all()
    for shipment in shipments:
        existing = db.query(StatusTracker).filter(StatusTracker.shipment_id == shipment.id).first()
        if not existing:
            tracker = StatusTracker(
                shipment_id=shipment.id,
                package_id=shipment.package_id,
                status=ShipmentStatus.PENDING,
                current_location=None,
                is_delivered=False,
            )
            db.add(tracker)
            print(f"[DEBUG] Created StatusTracker for shipment {shipment.id}")
    db.commit()
    print("[DEBUG] Finished creating missing StatusTrackers.")
