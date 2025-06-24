from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Body, Path, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from common.database import get_db
from shipment.api.v1.endpoints import routes
from user import views
from user.api.v1.models.address import Address
from user.views import (
    CountryService,
    UserService,
    signup_user,
)  # ✅ removed create_address
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
    ReplaceCountry,
    ReplaceUser,
    UpdateCountry,
    UpdateUser,
    SignUpRequest,
)


user_router = APIRouter()





# ======================= COUNTRIES =======================


@user_router.post("/create_country/", response_model=FetchCountry)
def create_country(country: CreateCountry, db: Session = Depends(get_db)):
    return CountryService.create_country(country, db)


@user_router.get("/countries/")
def get_all_countries(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return CountryService.get_all_countries(db=db, page=page, limit=limit)


@user_router.get("/countries/{country_id}", response_model=FetchCountry)
def get_country_by_id(country_id: int = Path(...), db: Session = Depends(get_db)):
    return CountryService.get_country_by_id(country_id, db)


@user_router.put("/replace_country/{country_id}", response_model=FetchCountry)
def replace_country(
    country_id: int, new_data: ReplaceCountry, db: Session = Depends(get_db)
):
    return CountryService.replace_country(country_id, new_data, db)


@user_router.patch("/update_country/{country_id}", response_model=FetchCountry)
def update_country(
    country_id: int, country_data: UpdateCountry, db: Session = Depends(get_db)
):
    return CountryService.update_country(country_id, country_data, db)
