from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, status

from passlib.context import CryptContext

from common.database import SessionLocal
from common.config import settings

from user.api.v1.utils.auth import create_access_token, create_refresh_token
from user.api.v1.models.users import User
from user.api.v1.schemas.user import CreateCountry, CreateUser, SignUpRequest, UpdateCountry, UpdateUser
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session
from fastapi import HTTPException

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
    def get_users(
        db: Session,
        user_id: int = None,
        email: str = None,
        user_type: str = None,
        is_active: bool = None,
        first_name: str = None,
    ):
        query = db.query(User)

        if user_id:
            user = query.filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404, detail="User with this ID not found"
                )
            return user

        if email:
            user = query.filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=404, detail="User with this email not found"
                )
            return user

        if user_type:
            query = query.filter(User.user_type == user_type)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if first_name:
            query = query.filter(User.first_name.ilike(f"%{first_name}%"))

        users = query.all()
        if not users:
            raise HTTPException(
                status_code=404, detail="No users found matching the criteria"
            )

        return users

    def update_user(user_id: int, user_data: UpdateUser, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        print(user, "::user")

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    def replace_user(user_id: int, user_data: CreateUser, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        for field, value in user_data.dict().items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user
    
    def disable_user(user_id: int, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
from user.api.v1.models.address import Address, Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session




# user/views/address_service.py or similar
from fastapi import HTTPException
from sqlalchemy.orm import Session
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress  # 👈 import your schema


class AddressService:

    @staticmethod
    def create_address(address_data: CreateAddress, db: Session):
        country = db.query(Country).filter(Country.id == address_data.country_code).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        address = Address(
            user_id=address_data.user_id,
            label=address_data.label,
            street_address=address_data.street_address,
            city=address_data.city,
            state=address_data.state,
            postal_code=address_data.postal_code,
            landmark=address_data.landmark,
            latitude=address_data.latitude,
            longitude=address_data.longitude,
            is_default=address_data.is_default,
            country=country
        )

        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def get_address_by_id(address_id: int, db: Session):
        address = db.query(Address).filter(Address.id == address_id).first()

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        if address.is_deleted:
            raise HTTPException(status_code=403, detail="Address has been deleted and cannot be fetched")

        return address

    @staticmethod
    def soft_delete_address(address_id: int, db: Session):
        address = db.query(Address).filter(Address.id == address_id).first()

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        if address.is_deleted:
            raise HTTPException(status_code=400, detail="Address is already deleted")

        address.is_deleted = True
        db.commit()
        db.refresh(address)
        return {"message": f"Address ID {address_id} has been soft deleted."}
 
    
    
class CountryService:
    @staticmethod
    def create_country(country_data: CreateCountry, db: Session):
        name = country_data.name.strip()

        if not name:
            raise HTTPException(status_code=400, detail="Country name cannot be null or empty")

        existing = db.query(Country).filter(
            func.lower(func.trim(Country.name)) == name.lower(),
            Country.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country = Country(name=name)
        db.add(country)
        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def get_all_countries(db: Session, page: int = 1, limit: int = 10):
        query = db.query(Country).filter(Country.is_deleted == False)
        total = query.count()
        countries = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": countries
        }

    @staticmethod
    def get_country_by_id(country_id: int, db: Session):
        country = db.query(Country).filter(
            Country.id == country_id,
            Country.is_deleted == False
        ).first()

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        return country


  
    @staticmethod
    
    def update_country(country_id: int, country_data: UpdateCountry, db: Session):
        country = db.query(Country).filter(
            Country.id == country_id,
            Country.is_deleted == False
        ).first()

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        # Handle soft delete
        if country_data.is_deleted is not None:
            country.is_deleted = country_data.is_deleted

        # Handle name update
        if country_data.name is not None:
            name = country_data.name.strip()
            if not name:
                raise HTTPException(status_code=400, detail="Country name cannot be null or empty")

            # Check for duplicates (exclude current)
            existing = db.query(Country).filter(
                Country.id != country_id,
                func.lower(func.trim(Country.name)) == name.lower(),
                Country.is_deleted == False
            ).first()

            if existing:
                raise HTTPException(status_code=400, detail="Country already exists")

            country.name = name

        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def replace_country(country_id: int, new_data: CreateCountry, db: Session):
        country = db.query(Country).filter(
            Country.id == country_id,
            Country.is_deleted == False
        ).first()

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        name = new_data.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Country name cannot be null or empty")

        # Check for duplicates (exclude current)
        existing = db.query(Country).filter(
            Country.id != country_id,
            func.lower(func.trim(Country.name)) == name.lower(),
            Country.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country.name = name

        db.commit()
        db.refresh(country)
        return country
