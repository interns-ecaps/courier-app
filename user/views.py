from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, Request, status

from passlib.context import CryptContext

from common.database import SessionLocal
from common.config import settings

from shipment.api.v1.models.payment import Payment, PaymentStatus
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.models.package import Package
from user.api.v1.utils.auth import create_access_token, create_refresh_token
from user.api.v1.models.users import User, UserType
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


from user.api.v1.models.address import Address, Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session


# user/views/address_service.py or similar
from fastapi import HTTPException
from sqlalchemy.orm import Session
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress  # 👈 import your schema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


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
        data={"sub": str(user.id)}, expires_delta=access_token_expires
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

    return {"user_id": new_user.id, "email": new_user.email}


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
        user_id = request.state.user.get("sub", None)

        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        if user_obj.user_type == "super_admin":
            query = db.query(User).filter(User.is_deleted == False)
        else:
            query = db.query(User).filter(User.id == user_id, User.is_deleted == False)

        if user_id:
            query = query.filter(User.id == user_id)

        if email:
            query = query.filter(User.email == email)

        if user_type:
            query = query.filter(User.user_type == user_type)

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

    # async def get_user_by_id(request, user_id: int, db: Session):
    #     user_id = request.state.user.get("sub", None)
    #     user_obj = (
    #         db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    #     )
    #     if not user_obj:
    #         raise HTTPException(status_code=404, detail="User not found")

    #     user = (
    #         db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    #     )

    #     if not user:
    #         raise HTTPException(status_code=404, detail="User not found")

    #     return FetchUser.model_validate(user)

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
        if user_data.is_deleted == False:
            if user_obj.user_type != "super_admin":
                raise HTTPException(status_code=403, detail="Only super admins can delete users")

        for field, value in user_data.dict(exclude_unset=True).items():
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
        city: Optional[str] = None,
        state: Optional[str] = None,
        country_code: Optional[int] = None,
        is_default: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        if address_id:
            address = (
                db.query(Address)
                .filter(Address.user_id == user_obj.id, Address.id == address_id)
                .first()
            )
            if not address:
                raise HTTPException(status_code=404, detail="Address not found")
            return FetchAddress.model_validate(address).model_dump()
        query = (
            db.query(Address)
            .options(joinedload(Address.user), joinedload(Address.country))
            .filter(Address.is_deleted == False)
        )

        if user_id is not None:
            query = query.filter(Address.user_id == user_id)

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

        # Handle is_deleted update separately
        if address.is_deleted and (update_data.is_deleted is not True):
            # Cannot update other fields of a soft-deleted address
            raise HTTPException(
                status_code=403,
                detail="Address has been deleted and cannot be updated",
            )

        for field, value in update_data.dict(exclude_unset=True).items():
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

        if  user_obj.user_type != "super_admin":
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
    async def get_dashboard_data(
        request,
        db: Session,
    ):
        # Fetch user from request.state.user
        user_id = request.state.user.get("sub", None)
        user_obj = (
            db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        print("User type:", user_obj.user_type)   # <-- add this line here

        user_type = user_obj.user_type

        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        # Shipments
        total_shipments = db.query(Shipment).filter(Shipment.is_deleted == False).count()
        shipments_today = db.query(Shipment).filter(
            Shipment.is_deleted == False,
            Shipment.created_at >= today
        ).count()
        shipments_this_month = db.query(Shipment).filter(
            Shipment.is_deleted == False,
            Shipment.created_at >= month_start
        ).count()

        # Payments
        total_payments = db.query(Payment).filter(Payment.is_deleted == False).count()
        pending_payments = db.query(Payment).filter(
            Payment.is_deleted == False,
            Payment.payment_status == PaymentStatus.PENDING
        ).count()
        completed_payments = db.query(Payment).filter(
            Payment.is_deleted == False,
            Payment.payment_status == PaymentStatus.COMPLETED
        ).count()

        # Users
        active_couriers = db.query(User).filter(
            User.is_deleted == False,
            User.is_active == True,
            User.user_type == "supplier"
        ).count()
        total_users = db.query(User).filter(User.is_deleted == False).count()

        # Prepare response
        dashboard_data = {
            "total_shipments": total_shipments,
            "shipments_today": shipments_today,
            "shipments_this_month": shipments_this_month,
            "total_payments": total_payments,
            "pending_payments": pending_payments,
            "completed_payments": completed_payments,
            "active_couriers": active_couriers,
            "total_users": total_users
        }

        
        # Add total revenue for everyone except super_admin
        if user_obj.user_type != "super_admin":
            total_revenue = db.query(
                func.coalesce(func.sum(Package.final_cost), 0)
            ).join(Payment.package).filter(
                Payment.is_deleted == False,
                Payment.payment_status == PaymentStatus.COMPLETED
            ).scalar()
            dashboard_data["total_revenue"] = float(total_revenue)

        return dashboard_data
    