from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, status

from passlib.context import CryptContext

from common.database import SessionLocal
from common.config import settings

from user.api.v1.utils.auth import create_access_token, create_refresh_token
from user.api.v1.models.users import User
from user.api.v1.schemas.user import CreateUser, SignUpRequest, UpdateUser

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