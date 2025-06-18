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
