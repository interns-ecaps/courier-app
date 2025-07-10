from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Form, HTTPException, Body, Path, Query, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from common.database import get_db
from core.decorators.token_required import token_required
from shipment.api.v1.endpoints import routes
from user import views
from user.api.v1.models.address import Address
from user.api.v1.models.users import UserType
from user.views import (
    CountryService,
    DashboardService,
    UserService,
    signup_user,
    AddressService
)
from user.api.v1.utils.auth import get_current_user
from user.api.v1.schemas.user import (
    CreateAddress,
    CreateCountry,
    CreateUser,
    FetchAddress,
    FetchCountry,
    FetchUser,
    ReplaceCountry,
    ReplaceUser,
    UpdateAddress,
    UpdateCountry,
    UpdateUser,
    SignUpRequest,
    ForgetPasswordRequest,
    ResetForgetPassword,
)
from common.config import settings
from fastapi_mail import ConnectionConfig

mail_conf = ConnectionConfig(
    MAIL_USERNAME = settings.smtp_user,
    MAIL_PASSWORD = settings.smtp_password,
    MAIL_FROM = settings.smtp_from_email,
    MAIL_PORT = settings.smtp_port,
    MAIL_SERVER = settings.smtp_host,
    MAIL_FROM_NAME = settings.smtp_from_email,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    TEMPLATE_FOLDER = './templates',
)

user_router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str


@user_router.get("/user-types")
def get_user_types():
    return [
        {"value": user_type.value,  "label": user_type.name.replace("_", " ").title()}
        for user_type in UserType if user_type != "super_admin"
    ]

@user_router.get("/read_profile/")
def read_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}


@user_router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return views.login_user(data.email, data.password, db)


@user_router.post("/signup")
def register_user(request: SignUpRequest, db: Session = Depends(get_db)):
    return signup_user(request, db)


@user_router.post("/create/")
def create_user(request: CreateUser, db: Session = Depends(get_db)):
    return views.UserService.create_user(request, db)


@user_router.get("/users/",)
@token_required
async def get_users(
    request: Request,
    email: Optional[str] = Query(default=None, description="Filter by email"),
    user_type: Optional[str] = Query(default=None, description="Filter by user type"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    first_name: Optional[str] = Query(default=None, description="Filter by first name"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, description="Items per page"),
    db: Session = Depends(get_db),
):
    
    return await UserService.get_users(
        request=request,
        db=db,
        email=email,
        user_type=user_type,
        is_active=is_active,
        first_name=first_name,
        page=page,
        limit=limit,
    )


@user_router.get("/users/{user_id}", response_model=FetchUser)
@token_required
async def get_user_by_id(request: Request,user_id: int, db: Session = Depends(get_db)):
    return await UserService.get_user_by_id(request, user_id=user_id, db=db)


@user_router.patch("/update_user/{user_id}")
@token_required
async def patch_user(
    request: Request,
    user_id: int,
    payload: UpdateUser = Body(...),  # <- ensures proper parsing of partial JSON
    db: Session = Depends(get_db),
):
    return await views.UserService.update_user(request, user_id, payload, db)


@user_router.put("/replace_user/{user_id}")
@token_required
async def replace_user(request: Request,user_id: int, payload: ReplaceUser, db: Session = Depends(get_db)):
    return await UserService.replace_user(request, user_id, payload, db)
@user_router.get("/user-types")
def get_user_types():
    return [
        {"value": user_type.value,  "label": user_type.name.replace("_", " ").title()}
        for user_type in UserType if user_type != "super_admin"
    ]



# ============================= ADDRESSES ==============================


@user_router.post("/create_address/", response_model=FetchAddress, status_code=201)
@token_required
async def create_address_route(request: Request,payload: CreateAddress, db: Session = Depends(get_db)):
    return await AddressService.create_address(request, payload, db)


@user_router.get("/addresses/", response_model=Union[dict, FetchAddress])
@token_required
async def get_all_addresses(
    request: Request,
    address_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    recipient_email: Optional[EmailStr] = Query(None, description="Fetch by recipient email"),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    country_code: Optional[int] = Query(None),
    is_default: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return await AddressService.get_addresses(
        request=request,
        db=db,
        address_id=address_id,
        user_id=user_id,
        recipient_email=recipient_email,
        city=city,
        state=state,
        country_code=country_code,
        is_default=is_default,
        page=page,
        limit=limit,
    )



@user_router.get("/addresses/{address_id}", response_model=FetchAddress)
@token_required
async def get_address_by_id(request: Request,address_id: int = Path(...), db: Session = Depends(get_db)):
    return await AddressService.get_address_by_id(request, address_id, db)


@user_router.patch("/update_address/{address_id}")
@token_required
async def update_address(
    request: Request,
    address_id: int,
    payload: UpdateAddress,
    db: Session = Depends(get_db),
):
    return await AddressService.update_address(request,address_id, payload, db)


@user_router.put("/replace_address/{address_id}", response_model=FetchAddress)
@token_required
async def replace_address_route(
    request: Request,address_id: int, payload: CreateAddress, db: Session = Depends(get_db)
):
    return await AddressService.replace_address(request,address_id, payload, db)


# ======================= COUNTRIES =======================


@user_router.post("/create_country/", response_model=FetchCountry)
@token_required
async def create_country(request: Request,country: CreateCountry, db: Session = Depends(get_db)):
    return await CountryService.create_country(request, country, db)


@user_router.get("/countries/")
@token_required
async def get_all_countries(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return await CountryService.get_all_countries(request, db=db, page=page, limit=limit)


@user_router.get("/countries/{country_id}", response_model=FetchCountry)
@token_required
async def get_country_by_id(request: Request,country_id: int = Path(...), db: Session = Depends(get_db)):
    return await CountryService.get_country_by_id(country_id, db)


@user_router.put("/replace_country/{country_id}", response_model=FetchCountry)
@token_required
async def replace_country(
    request: Request,country_id: int, new_data: ReplaceCountry, db: Session = Depends(get_db)
):
    return await CountryService.replace_country(request, country_id, new_data, db)


@user_router.patch("/update_country/{country_id}", response_model=FetchCountry)
@token_required
async def update_country(
    request: Request,country_id: int, country_data: UpdateCountry, db: Session = Depends(get_db)
):
    return await CountryService.update_country(request, country_id, country_data, db)

@user_router.get("/dashboard")
@token_required
async def get_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    start_date: str = Query(None, description="Optional start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="Optional end date in YYYY-MM-DD format")
):
    user_info = getattr(request.state, "user", None)
    return await DashboardService.get_dashboard_data(request, db, user_info, start_date, end_date)

@user_router.post("/forget-password")
async def forget_password_route(
    background_tasks: BackgroundTasks,
    fpr: ForgetPasswordRequest,
    db: Session = Depends(get_db),
):
    return await views.forget_password(background_tasks, fpr, db, mail_conf)

@user_router.post("/reset-password")
async def reset_password_route(
    rfp: ResetForgetPassword,
    db: Session = Depends(get_db),
):
    return await views.reset_password(rfp, db)


@user_router.get("/test-email-config")
async def test_email_config():
    """Test endpoint to check email configuration"""
    return {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user,
        "smtp_from_email": settings.smtp_from_email,
        "app_host": settings.APP_HOST,
        "forget_password_url": settings.FORGET_PASSWORD_URL,
        "config_loaded": True
    }