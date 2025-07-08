from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, extract
from pydantic import EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, Query, Request, status

from passlib.context import CryptContext

from common.database import SessionLocal
from common.config import settings

from shipment.api.v1.models.payment import Payment, PaymentStatus
from shipment.api.v1.models.shipment import Shipment
from user.api.v1.utils.auth import create_access_token, create_refresh_token
from user.api.v1.models.users import User
from user.api.v1.schemas.user import (
    CreateCountry,
    CreateUser,
    FetchAddress,
    FetchCountry,
    FetchUser,
    SignUpRequest,
    UpdateAddress,
    UpdateCountry,
    UpdateUser,
)
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session
from fastapi import HTTPException

from shipment.api.v1.models.status import StatusTracker, ShipmentStatus

from user.api.v1.models.address import Address, Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session

from shipment.api.v1.models.package import Package

# user/views/address_service.py or similar
from fastapi import HTTPException
from sqlalchemy.orm import Session
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress  # 👈 import your schema



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    print(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def login_user(email: str, password: str, db: Session):
    # 1. Fetch the user from the DB
    user = db.query(User).filter(User.email == email).first()

    # 2. Check if user exists
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3. Verify the password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 4. Create JWT tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = settings.refresh_token_expire_days

    access_token = create_access_token(
    data={"sub": str(user.id), "user_type": user.user_type}, expires_delta=access_token_expires
)

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_days=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
        },
        "success": True,
    }


def signup_user(user_data: SignUpRequest, db: Session):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        user_type=user_data.user_type,
        # is_active=True,
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user_id": new_user.id, "email": new_user.email, "success": True}


class UserService:
    def create_user(user_data: CreateUser, db: Session):
        try:
            new_user = User(**user_data.dict())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this information already exists or required fields are missing.",
            )
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating the user.",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_users(
        request: Request,
        db: Session,
        email: Optional[str] = None,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        first_name: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ):
        current_user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User)
            .filter(User.id == current_user_id, User.is_deleted == False)
            .first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # 1) Super‑admins can see everyone
        if user_obj.user_type == "super_admin":
            query = db.query(User).filter(User.is_deleted == False)

        # 2) Non‑admins requesting suppliers → all suppliers
        elif user_type == "supplier":
            query = (
                db.query(User)
                .filter(
                    User.is_deleted == False,
                    User.user_type == "supplier",
                )
            )

        # 3) Everyone else → only self
        else:
            query = (
                db.query(User)
                .filter(
                    User.is_deleted == False,
                    User.id == current_user_id,
                )
            )

        # Apply additional filters *only* if they were supplied
        if email:
            query = query.filter(User.email == email)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if first_name:
            query = query.filter(User.first_name.ilike(f"%{first_name}%"))

        total = query.count()
        users = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchUser.model_validate(u) for u in users],
        }


    async def get_user_by_id(request, user_id: int, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        user = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return FetchUser.model_validate(user)

    @staticmethod
    async def update_user(request, user_id: int, user_data: UpdateUser, db: Session):
        # user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found.")

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Optional: Add unique constraint check for email
        if user_data.email and user_data.email != user_obj.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already in use.")

        # Only super_admin can soft delete
        # if user_data.is_deleted == False:
        #     if user_obj.user_type != "super_admin":
        #         raise HTTPException(status_code=403, detail="Only super admins can delete users")

        for field, value in user_data.dict(exclude_unset=True).items():
            if field == "password":
                if not verify_password(user_data.current_password, user_obj.hashed_password):
                    raise HTTPException(status_code=400, detail="Incorrect password")
                print(value, "::value")
                hashed = hash_password(value)
                setattr(user_obj, "hashed_password", hashed)
            else:
                setattr(user_obj, field, value)

        db.commit()
        db.refresh(user_obj)
        return FetchUser.model_validate(user_obj)

    async def replace_user(request, user_id: int, user_data: CreateUser, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        for field, value in user_data.dict().items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user


class AddressService:

    @staticmethod
    async def create_address(request, address_data: CreateAddress, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        country = (
            db.query(Country).filter(Country.id == address_data.country_code).first()
        )
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        # Latitude and longitude validation
        if address_data.latitude is not None and not (
            -90 <= address_data.latitude <= 90
        ):
            raise HTTPException(
                status_code=400, detail="Latitude must be between -90 and 90."
            )

        if address_data.longitude is not None and not (
            -180 <= address_data.longitude <= 180
        ):
            raise HTTPException(
                status_code=400, detail="Longitude must be between -180 and 180."
            )

        address = Address(
            user_id=user_obj.id,
            label=address_data.label,
            street_address=address_data.street_address,
            city=address_data.city,
            state=address_data.state,
            postal_code=address_data.postal_code,
            landmark=address_data.landmark,
            latitude=address_data.latitude,
            longitude=address_data.longitude,
            is_default=address_data.is_default,
            country=country,
        )

        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    async def get_addresses(
        request,
        db: Session,
        address_id: Optional[int] = None,
        user_id: Optional[int] = None,
        recipient_email: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country_code: Optional[int] = None,
        is_default: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        current_user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User)
            .filter(User.id == current_user_id, User.is_deleted == False)
            .first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # 👇 New logic: convert recipient_email → user_id
        if recipient_email:
            recipient = (
                db.query(User)
                .filter(User.email == recipient_email, User.is_deleted == False)
                .first()
            )
            if not recipient:
                raise HTTPException(status_code=404, detail="Recipient not found")
            user_id = recipient.id  # ← override user_id for address filter

        # ─────────────────────────────────────────────
        query = (
            db.query(Address)
            .options(joinedload(Address.user), joinedload(Address.country))
            .filter(Address.is_deleted == False)
            .order_by(Address.is_default.desc(), Address.updated_at.desc())
        )

        # 1) Non‑admins can only see their own addresses
        if user_obj.user_type != "super_admin":
            query = query.filter(Address.user_id == current_user_id)
        # 2) Super‑admins can pass ?user_id= or ?recipient_email=
        elif user_id is not None:
            query = query.filter(Address.user_id == user_id)

        # 3) Single address lookup
        if address_id:
            address = query.filter(Address.id == address_id).first()
            if not address:
                raise HTTPException(status_code=404, detail="Address not found")
            return FetchAddress.model_validate(address).model_dump()

        # 4) Additional filters
        if city:
            query = query.filter(Address.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Address.state.ilike(f"%{state}%"))
        if country_code is not None:
            query = query.filter(Address.country_code == country_code)
        if is_default is not None:
            query = query.filter(Address.is_default == is_default)

        total = query.count()
        addresses = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": [FetchAddress.model_validate(a) for a in addresses],
        }


    @staticmethod
    async def get_address_by_id(request, address_id: int, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        address = db.query(Address).filter(Address.id == address_id).first()

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        if address.is_deleted:
            raise HTTPException(
                status_code=403, detail="Address has been deleted and cannot be fetched"
            )

        return address

    @staticmethod
    async def update_address(
        request, address_id: int, update_data: UpdateAddress, db: Session
    ):
        user_id = request.state.user.get("sub", None)

        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        address = (
            db.query(Address)
            .filter(Address.user_id == user_obj.id, Address.id == address_id)
            .first()
        )
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        if address.is_deleted and (update_data.is_deleted is not True):
            raise HTTPException(
                status_code=403,
                detail="Address has been deleted and cannot be updated",
            )

        update_fields = update_data.dict(exclude_unset=True)

        # 🟡 CRUCIAL: This part must exist!
        if update_fields.get("is_default", False) is True:
            db.query(Address).filter(
                Address.user_id == user_obj.id,
                Address.id != address_id,
                Address.is_deleted == False
            ).update({"is_default": False})

        for field, value in update_fields.items():
            setattr(address, field, value)

        db.commit()
        db.refresh(address)

        return {"message": "Address updated successfully", "address": address}



    @staticmethod
    async def replace_address(
        request, address_id: int, address_data: CreateAddress, db: Session
    ):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        address = (
            db.query(Address)
            .filter(Address.user_id == user_obj.id, Address.id == address_id)
            .first()
        )

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        for field, value in address_data.dict().items():
            setattr(address, field, value)

        db.commit()
        db.refresh(address)
        return address


# ========================== COUNTRY =========================


class CountryService:
    @staticmethod
    async def create_country(request, country_data: CreateCountry, db: Session):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can create countries"
            )

        name = country_data.name.strip()

        if not name:
            raise HTTPException(
                status_code=400, detail="Country name cannot be null or empty"
            )

        existing = (
            db.query(Country)
            .filter(
                func.lower(func.trim(Country.name)) == name.lower(),
                Country.is_deleted == False,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country = Country(name=name)
        db.add(country)
        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    async def get_all_countries(request, db: Session, page: int = 1, limit: int = 10):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        query = db.query(Country).filter(Country.is_deleted == False)
        total = query.count()
        countries = query.offset((page - 1) * limit).limit(limit).all()

        return {"page": page, "limit": limit, "total": total, "results": countries}

    # Adjust import if needed

    # @staticmethod
    # async def get_country_by_id(country_id: int, db: Session) -> FetchCountry:
    #     country = (
    #         db.query(Country)
    #         .filter(Country.id == country_id, Country.is_deleted == False)
    #         .first()
    #     )

    #     if not country:
    #         raise HTTPException(status_code=404, detail="Country not found")

    #     return FetchCountry.model_validate(country)

    @staticmethod
    async def update_country(
        request, country_id: int, country_data: UpdateCountry, db: Session
    ):

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can edit countries"
            )

        country = (
            db.query(Country)
            .filter(Country.id == country_id, Country.is_deleted == False)
            .first()
        )

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        # Handle soft delete
        if country_data.is_deleted is not None:
            country.is_deleted = country_data.is_deleted

        # Handle name update
        if country_data.name is not None:
            name = country_data.name.strip()
            if not name:
                raise HTTPException(
                    status_code=400, detail="Country name cannot be null or empty"
                )

            # Check for duplicates (exclude current)
            existing = (
                db.query(Country)
                .filter(
                    Country.id != country_id,
                    func.lower(func.trim(Country.name)) == name.lower(),
                    Country.is_deleted == False,
                )
                .first()
            )

            if existing:
                raise HTTPException(status_code=400, detail="Country already exists")

            country.name = name

        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    async def replace_country(
        request, country_id: int, new_data: CreateCountry, db: Session
    ):

        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type != "super_admin":
            raise HTTPException(
                status_code=403, detail="Only admin users can edit countries"
            )

        country = (
            db.query(Country)
            .filter(Country.id == country_id, Country.is_deleted == False)
            .first()
        )

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        name = new_data.name.strip()
        if not name:
            raise HTTPException(
                status_code=400, detail="Country name cannot be null or empty"
            )

        # Check for duplicates (exclude current)
        existing = (
            db.query(Country)
            .filter(
                Country.id != country_id,
                func.lower(func.trim(Country.name)) == name.lower(),
                Country.is_deleted == False,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country.name = name

        db.commit()
        db.refresh(country)
        return country


class DashboardService:
    @staticmethod
    async def get_dashboard_data(request, db, user_info):
        if not user_info:
            raise HTTPException(status_code=401, detail="User info missing")

        user_type = user_info.get("user_type")
        user_id = int(user_info.get("sub"))  # Ensure user_id is int for queries

        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        # Helper queries
        def shipments_query():
            return db.query(Shipment).filter(Shipment.is_deleted == False)

        def payments_query():
            return db.query(Payment).filter(Payment.is_deleted == False)

        def packages_query():
            return db.query(Package).filter(Package.is_deleted == False)

        # Super Admin Dashboard
        if user_type == "super_admin":
            return {
                "total_shipments": shipments_query().count(),
                "shipments_today": shipments_query().filter(Shipment.created_at >= today).count(),
                "shipments_this_month": shipments_query().filter(Shipment.created_at >= month_start).count(),
                "active_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    StatusTracker.status.in_([ShipmentStatus.IN_TRANSIT, ShipmentStatus.PENDING])
                ).count(),
                "delivered_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    StatusTracker.status == ShipmentStatus.DELIVERED
                ).count(),
                "total_packages": packages_query().count(),
                "pending_payments": payments_query().filter(Payment.payment_status == PaymentStatus.PENDING).count(),
                "completed_payments": payments_query().filter(Payment.payment_status == PaymentStatus.COMPLETED).count(),
                "total_payments": payments_query().count(),
                "total_users": db.query(User).filter(User.is_deleted == False).count(),
                "active_users": db.query(User).filter(User.is_active == True, User.is_deleted == False).count(),
                "recent_shipments": [s.id for s in shipments_query().order_by(Shipment.created_at.desc()).limit(5)],
                "shipments_per_month": get_shipments_per_month(db, user_type, user_id),
                "revenue_per_month": get_revenue_per_month(db, user_type, user_id),
                "top_performing_suppliers": get_top_performing_suppliers(db),
                # Add analytics as needed
            }

        # Supplier Dashboard
        elif user_type == "supplier":
            return {
                "total_shipments_created": shipments_query().filter(Shipment.sender_id == user_id).count(),
                "shipments_today": shipments_query().filter(Shipment.sender_id == user_id, Shipment.created_at >= today).count(),
                "shipments_this_month": shipments_query().filter(Shipment.sender_id == user_id, Shipment.created_at >= month_start).count(),
                "pending_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    Shipment.sender_id == user_id,
                    StatusTracker.status.in_([ShipmentStatus.IN_TRANSIT, ShipmentStatus.PENDING])
                ).count(),
                "delivered_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    Shipment.sender_id == user_id,
                    StatusTracker.status == ShipmentStatus.DELIVERED
                ).count(),
                # Payments expected to receive (as supplier = sender)
                "pending_payments": db.query(Payment).join(Shipment).filter(
                    Shipment.sender_id == user_id,
                    Payment.payment_status == PaymentStatus.PENDING
                ).count(),
                "completed_payments": db.query(Payment).join(Shipment).filter(
                    Shipment.sender_id == user_id,
                    Payment.payment_status == PaymentStatus.COMPLETED
                ).count(),
                "total_revenue": db.query(func.sum(Package.final_cost)).join(Payment).join(Shipment).filter(
                    Shipment.sender_id == user_id,
                    Payment.payment_status == PaymentStatus.COMPLETED
                ).scalar() or 0,
                "shipments_per_month": get_shipments_per_month(db, user_type, user_id),
                "revenue_per_month": get_revenue_per_month(db, user_type, user_id),
            }

        # Importer/Exporter Dashboard
        elif user_type == "importer_exporter":
            return {
                "total_shipments": shipments_query().filter(
                    (Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id)
                ).count(),
                "shipments_imported": shipments_query().filter(Shipment.recipient_id == user_id).count(),
                "shipments_exported": shipments_query().filter(Shipment.sender_id == user_id).count(),
                "shipments_today": shipments_query().filter(
                    ((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id)),
                    Shipment.created_at >= today
                ).count(),
                "shipments_this_month": shipments_query().filter(
                    ((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id)),
                    Shipment.created_at >= month_start
                ).count(),
                "active_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    ((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id)),
                    StatusTracker.status.in_([ShipmentStatus.IN_TRANSIT, ShipmentStatus.PENDING])
                ).count(),
                "delivered_shipments": db.query(Shipment).join(StatusTracker).filter(
                    Shipment.is_deleted == False,
                    ((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id)),
                    StatusTracker.status == ShipmentStatus.DELIVERED
                ).count(),
                # Payments made by this user (as importer/exporter = recipient)
                "total_payments_made": db.query(Payment).join(Shipment).filter(
                    Shipment.recipient_id == user_id,
                    Payment.payment_status == PaymentStatus.COMPLETED
                ).count(),
                "pending_payments": db.query(Payment).join(Shipment).filter(
                    Shipment.recipient_id == user_id,
                    Payment.payment_status == PaymentStatus.PENDING
                ).count(),
                "completed_payments": db.query(Payment).join(Shipment).filter(
                    Shipment.recipient_id == user_id,
                    Payment.payment_status == PaymentStatus.COMPLETED
                ).count(),
                "addresses_count": db.query(Address).filter(Address.user_id == user_id).count(),
                "shipments_per_month": get_shipments_per_month(db, user_type, user_id),
                "revenue_per_month": get_revenue_per_month(db, user_type, user_id),
                # Add suppliers/partners count as needed
            }

        else:
            raise HTTPException(status_code=403, detail="Unauthorized dashboard access")

def get_shipments_per_month(db, user_type, user_id):
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()
    months = []
    counts = []
    for i in range(5, -1, -1):  # Last 6 months
        first_day = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        query = db.query(Shipment).filter(
            Shipment.created_at >= first_day,
            Shipment.created_at <= last_day,
            Shipment.is_deleted == False
        )
        if user_type == "supplier":
            query = query.filter(Shipment.sender_id == user_id)
        elif user_type == "importer_exporter":
            query = query.filter((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id))
        # super_admin sees all
        months.append(first_day.strftime("%b %Y"))
        counts.append(query.count())
    return {"labels": months, "data": counts}

def get_revenue_per_month(db, user_type, user_id):
    from datetime import datetime, timedelta
    months = []
    revenue = []
    today = datetime.utcnow().date()
    for i in range(5, -1, -1):  # Last 6 months
        first_day = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        query = db.query(func.sum(Package.final_cost)).join(Payment).join(Shipment).filter(
            Shipment.created_at >= first_day,
            Shipment.created_at <= last_day,
            Payment.payment_status == PaymentStatus.COMPLETED
        )
        if user_type == "supplier":
            query = query.filter(Shipment.sender_id == user_id)
        elif user_type == "importer_exporter":
            query = query.filter((Shipment.sender_id == user_id) | (Shipment.recipient_id == user_id))
        # super_admin sees all
        months.append(first_day.strftime("%b %Y"))
        revenue.append(float(query.scalar() or 0))
    return {"labels": months, "data": revenue}

def get_top_performing_suppliers(db, limit=5):
    # Show top performers regardless of user type
    top_suppliers = db.query(
        User.first_name,
        User.last_name,
        User.user_type,  # Add this to see user type
        func.sum(Package.final_cost).label('total_revenue'),
        func.count(Shipment.id).label('total_shipments')
    ).join(Shipment, User.id == Shipment.sender_id)\
     .join(Payment, Shipment.id == Payment.shipment_id)\
     .join(Package, Payment.package_id == Package.id)\
     .filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        User.is_deleted == False
        # Remove the supplier filter to include all user types
     )\
     .group_by(User.id, User.first_name, User.last_name, User.user_type)\
     .order_by(func.sum(Package.final_cost).desc())\
     .limit(limit)\
     .all()
    
    return [
        {
            "name": f"{supplier.first_name} {supplier.last_name}",
            "user_type": supplier.user_type,  # Include user type
            "revenue": float(supplier.total_revenue or 0),
            "shipments": supplier.total_shipments
        }
        for supplier in top_suppliers
    ]