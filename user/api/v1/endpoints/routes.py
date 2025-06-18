from fastapi import (
    APIRouter,Depends, Form, HTTPException
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from common.database import get_db
from user import views
from user.views import login_user
from user.api.v1.utils.auth import get_current_user


from user.views import get_db  # this can be a no-op temporarily


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

