from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from passlib.context import CryptContext

from user.api.v1.models.users import User
from user.api.v1.schemas.user import CreateUser, SignUpUser, UpdateUser
from user.api.v1.utils.auth import create_access_token, create_refresh_token
from common.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user or not UserService.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_days=settings.refresh_token_expire_days
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def signup_user(user_data: SignUpUser, db: Session):
        email = user_data.email
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        try:
            hashed_password = UserService.hash_password(user_data.password)
            new_user = User(
                email=email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                hashed_password=hashed_password,
                phone_number=user_data.phone_number,
                user_type=user_data.user_type,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            access_token = create_access_token(
                data={"sub": str(new_user.id)},
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
            )
            refresh_token = create_refresh_token(
                data={"sub": str(new_user.id)},
                expires_days=settings.refresh_token_expire_days
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
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
                status_code=400,
                detail="User with this information already exists or required fields are missing.",
            )
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while creating the user.",
            )

    @staticmethod
    def update_user(user_id: int, user_data: UpdateUser, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def replace_user(user_id: int, user_data: CreateUser, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        for field, value in user_data.dict().items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

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
                raise HTTPException(status_code=404, detail="User with this ID not found")
            return user

        if email:
            user = query.filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User with this email not found")
            return user

        if user_type:
            query = query.filter(User.user_type == user_type)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if first_name:
            query = query.filter(User.first_name.ilike(f"%{first_name}%"))

        users = query.all()
        if not users:
            raise HTTPException(status_code=404, detail="No users found matching the criteria")

        return users
