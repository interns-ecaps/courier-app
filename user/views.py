from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from common.database import SessionLocal
from user.api.v1.utils.auth import create_access_token,create_refresh_token
from user.api.v1.models.users import User  # ✅ Correct import
from passlib.context import CryptContext
from common.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def login_user(email: str, password: str, db=None):  # db not used temporarily
    # TEMPORARY MOCK AUTH
    if email != "test@example.com" or password != "123456":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = settings.refresh_token_expire_days

    access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": email}, expires_days=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# user/views.py (continued)

mock_users = {}  # TEMP in-memory storage: {email: hashed_password}

def signup_user(email: str, password: str):
    if email in mock_users:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    mock_users[email] = hashed_password  # save mock user

    # generate tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = settings.refresh_token_expire_days

    access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": email}, expires_days=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }









#---------------------------------------------------#


# def login_user(email: str, password: str, db: Session):
#     db_user = db.query(User).filter(User.email == email).first()  # ✅ email, not username

#     if not db_user or not verify_password(password, db_user.hashed_password):  # ✅ hashed_password
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
#     access_token = create_access_token(
#         data={"sub": str(db_user.id)},  # ✅ assuming 'id' is your primary key
#         expires_delta=access_token_expires
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }
from user.api.v1.models.users import User
from user.api.v1.schemas.user import CreateUser, UpdateUser
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status


class UserService:
    def create_user(user_data: CreateUser, db: Session):
        try:
            new_user = User(**user_data.dict())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this information already exists or required fields are missing."
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating the user."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    

    @staticmethod
    def get_users(
        db: Session,
        user_id: int = None,
        email: str = None,
        user_type: str = None,
        is_active: bool = None,
        first_name: str = None
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
