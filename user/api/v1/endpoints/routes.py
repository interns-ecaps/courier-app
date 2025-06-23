from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Body, Path, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from common.database import get_db
from shipment.api.v1.endpoints import routes
from user import views
from user.api.v1.models.address import Address
from user.views import CountryService, UserService, signup_user  # ✅ removed create_address
from user.views import AddressService  # ✅ imported from correct file

from user.api.v1.utils.auth import get_current_user
from user.views import AddressService



from user import views
from user.api.v1.schemas.user import (
    CreateAddress,
    CreateCountry,
    CreateUser,
    FetchAddress,
    FetchCountry,
    FetchUser,
    ReplaceUser,
    UpdateCountry,
    UpdateUser,
    SignUpRequest,
)


user_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


# @user_router.get("/health_check/")
# def health_check():
#     return {"status": "actived", "message": "User Service is up and running"}


@user_router.get("/read_profile/")
def read_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}


@user_router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return views.login_user(data.email, data.password, db)


@user_router.post("/signup")
def register_user(request: SignUpRequest, db: Session = Depends(get_db)):
    return signup_user(request, db)


@user_router.post("/create_user/")
def create_user(request: CreateUser, db: Session = Depends(get_db)):
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
    result = UserService.get_users(
        db=db,
        user_id=user_id,
        email=email,
        user_type=user_type,
        is_active=is_active,
        first_name=first_name,
    )

    if isinstance(result, list):
        return result
    return [result]


@user_router.patch("/update_user/{user_id}")
def patch_user(
    user_id: int,
    request: UpdateUser = Body(...),  # <- ensures proper parsing of partial JSON
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return views.UserService.update_user(user_id, request, db)


@user_router.put("/replace_user/{user_id}")
def replace_user(user_id: int, request: ReplaceUser, db: Session = Depends(get_db)):
    return UserService.replace_user(user_id, request, db)


@user_router.patch("/disable_user/{user_id}")
def disable_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.disable_user(user_id, db) 


@user_router.post("/addresses/", response_model=FetchAddress, status_code=201)
def create_address_route(payload: CreateAddress, db: Session = Depends(get_db)):
    return AddressService.create_address(payload, db)

@user_router.get("/addresses", response_model=FetchAddress)
def get_address(id: int = Query(...), db: Session = Depends(get_db)):
    return AddressService.get_address_by_id(id, db)
@user_router.delete("/addresses", status_code=200)
def delete_address(
    address_id: int = Query(..., alias="id", description="ID of the address to soft delete"),
    db: Session = Depends(get_db),
):
    return AddressService.soft_delete_address(address_id, db)


@user_router.post("/create_country/", response_model=FetchCountry)
def create_country(country: CreateCountry, db: Session = Depends(get_db)):
    return CountryService.create_country(country, db)

@user_router.get("/countries/")
def get_all_countries(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return CountryService.get_all_countries(db=db, page=page, limit=limit)

@user_router.get("/countries/{country_id}", response_model=FetchCountry)
def get_country_by_id(country_id: int = Path(...), db: Session = Depends(get_db)):
    return CountryService.get_country_by_id(country_id, db)

@user_router.put("/replace_country/{country_id}", response_model=FetchCountry)
def replace_country(country_id: int, new_data: CreateCountry, db: Session = Depends(get_db)):
    return CountryService.replace_country(country_id, new_data, db)

@user_router.patch("/update_country/{country_id}", response_model=FetchCountry)
def update_country(country_id: int, country_data: UpdateCountry, db: Session = Depends(get_db)):
    return CountryService.update_country(country_id, country_data, db)
