from fastapi import (
    APIRouter, Body, Depends, HTTPException,Query
)
from shipment import views
from fastapi import Request, Depends, Path
from sqlalchemy.orm import Session
from common.database import get_db
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage,FetchPackage, UpdatePackage
from typing import Optional, List
shipment_router = APIRouter()


# ================================ CURRENCY =====================================


@shipment_router.post("/create_currency/")
def create_currency(request: CreateCurrency, db: Session = Depends(get_db)):
    return views.CurrencyService.create_currency(request, db)


# =============================== PACKAGE ==========================================


@shipment_router.post("/create_package/")
def create_package(request: CreatePackage, db: Session = Depends(get_db)):
    return views.PackageService.create_package(request, db)

@shipment_router.get("/packages/")
def get_packages(
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return views.PackageService.get_packages(
        db=db,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        page=page,
        limit=limit
    )

@shipment_router.get("/packages/{package_id}", response_model=FetchPackage)
def get_package_by_id(
    package_id: int = Path(..., description="The ID of the package to retrieve"),
    db: Session = Depends(get_db),
):
    return views.PackageService.get_package_by_id(package_id, db)

@shipment_router.patch("/update_package/{package_id}")
def patch_user(
    package_id: int,
    request: UpdatePackage = Body(...),  # <- ensures proper parsing of partial JSON
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return views.PackageService.update_package(package_id, request, db)
