from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


from common.database import get_db
from shipment.api.v1.models.shipment import Role, User
from shipment.api.v1.schemas.sales_dashboard import TokenData
from common.config import settings

# from .database import get_db

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

print(oauth2_scheme, ":::oauth2_scheme")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, email: str = None, username: str = None):
    if email:
        return db.query(User).filter(User.email == email).first()
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superadmin_user(
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


# Check user permissions
def user_has_permission(user: User, permission_name: str, db: Session) -> bool:
    if user.is_superadmin:
        return True

    for role in user.roles:
        for permission in role.permissions:
            if permission.name == permission_name:
                return True

    return False


# Helper function to check permissions as a dependency
def has_permission(permission_name: str):
    def check_permission(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ):
        if not user_has_permission(current_user, permission_name, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions: {permission_name} required",
            )
        return current_user

    return check_permission


# Helper function to check permissions as a dependency
def has_permission(permission_name: str):
    def check_permission(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ):
        if not user_has_permission(current_user, permission_name, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions: {permission_name} required",
            )
        return current_user

    return check_permission


def get_user_and_subordinates(db: Session, user_id: int):
    """
    Recursive function to get a user and all their subordinates.
    """
    user = (
        db.query(User)
        .options(
            joinedload(User.state),
            joinedload(User.states),
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.department),
        )
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        return []
    result = [user]
    subordinates = (
        db.query(User)
        .options(
            joinedload(User.state),
            joinedload(User.states),
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.department),
        )
        .filter(User.parent_id == user_id)
        .all()
    )

    # Recursively get subordinates of subordinates
    for subordinate in subordinates:
        result.extend(get_user_and_subordinates(db, subordinate.id))

    return result


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.is_superadmin:
        return current_user

    for role in current_user.roles:
        for permission in role.permissions:
            if permission.name in [
                "create_user",
                "update_user",
                "delete_user",
                "manage_roles",
                "assign_permission",
            ]:
                return current_user

    # If no admin permissions found, raise a 403 Forbidden exception
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Administrator privileges required for this operation",
    )
