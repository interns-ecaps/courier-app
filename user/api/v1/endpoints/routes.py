from fastapi import (
    APIRouter,Depends, Form, HTTPException, Body, Query
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from common.database import get_db
from user import views
from user.views import login_user
from user.api.v1.utils.auth import get_current_user


from user.views import get_db  # this can be a no-op temporarily
from shipment import views
from user.api.v1.schemas.user import CreateUser, FetchUser, ReplaceUser, UpdateUser
from user import views
from sqlalchemy.orm import Session
from common.database import get_db


user_router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str


@user_router.get("/health_check/")
def health_check():
    return {"status": "active", "message": "User Service is up and running"}
@user_router.get("/read_profile/")
def read_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}

@user_router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return views.login_user(data.email, data.password, db)

# user/api/v1/endpoints/routes.py

class SignupRequest(BaseModel):
    email: str
    password: str

@user_router.post("/signup")
def signup(data: SignupRequest):
    return views.signup_user(data.email, data.password)



@user_router.post("/create_user/")
def create_user(request:CreateUser, db: Session = Depends(get_db)):
    return views.UserService.create_user(request, db)

@user_router.get("/get_user/", response_model=list[FetchUser])
def get_users(
    user_id: int = None,
    email: str = None,
    user_type: str = Query(default=None, description="Filter by user type"),
    is_active: bool = Query(default=None, description="Filter by active status"),
    first_name: str = Query(default=None, description="Filter by first name"),
    db: Session = Depends(get_db),
):
    result = views.UserService.get_users(
        db=db,
        user_id=user_id,
        email=email,
        user_type=user_type,
        is_active=is_active,
        first_name=first_name
    )

    if isinstance(result, list):
        return result
    return [result]
@user_router.patch("/update_user/{user_id}")
def patch_user(
    user_id: int,
    request: UpdateUser = Body(...),  # <- ensures proper parsing of partial JSON
    db: Session = Depends(get_db)
):
    print(request.dict(exclude_unset=False))
    return views.UserService.update_user(user_id, request, db)

@user_router.put("/replace_user/{user_id}")
def replace_user(user_id: int, request: ReplaceUser, db: Session = Depends(get_db)):
    return views.UserService.replace_user(user_id, request, db)
