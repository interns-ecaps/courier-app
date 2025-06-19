from fastapi import APIRouter, Depends, Body, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.database import get_db
from user.views import UserService
from user.api.v1.utils.auth import get_current_user
from user.api.v1.schemas.user import (
    CreateUser,
    FetchUser,
    # ReplaceUser,
    UpdateUser,
    SignUpUser,
)

user_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@user_router.get("/read_profile/")
def read_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}


@user_router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return UserService.login_user(data.email, data.password, db)


@user_router.post("/signup")
def signup(data: SignUpUser, db: Session = Depends(get_db)):
    return UserService.signup_user(data, db)


@user_router.post("/create_user/")
def create_user(request: CreateUser, db: Session = Depends(get_db)):
    return UserService.create_user(request, db)


@user_router.get("/get_user/", response_model=list[FetchUser])
def get_users(
    user_id: int = None,
    email: str = None,
    user_type: str = Query(default=None, description="Filter by user type"),
    is_active: bool = Query(default=None, description="Filter by active status"),
    first_name: str = Query(default=None, description="Filter by first name"),
    db: Session = Depends(get_db),
):
    result = UserService.get_users(
        db=db,
        user_id=user_id,
        email=email,
        user_type=user_type,
        is_active=is_active,
        first_name=first_name,
    )

    return result if isinstance(result, list) else [result]


@user_router.patch("/update_user/{user_id}")
def patch_user(
    user_id: int,
    request: UpdateUser = Body(...),
    db: Session = Depends(get_db),
):
    return UserService.update_user(user_id, request, db)


@user_router.put("/replace_user/{user_id}")
def replace_user(user_id: int, request: ReplaceUser, db: Session = Depends(get_db)):
    return UserService.replace_user(user_id, request, db)
