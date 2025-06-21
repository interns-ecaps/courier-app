from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from common.database import get_db
from shipment import views
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    UpdatePackage,
    FetchPackage,
    FetchCurrency,
    UpdateShipment,
)

shipment_router = APIRouter()

# ================================ SHIPMENT =====================================


@shipment_router.post("/create_shipment/")
def create_shipment(request: CreateShipment, db: Session = Depends(get_db)):
    return views.ShipmentService.create_shipment(request, db)


@shipment_router.get("/shipments/")
def get_shipments(
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    shipment_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return views.ShipmentService.get_shipments(
        db=db,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        shipment_type=shipment_type,
        page=page,
        limit=limit,
    )


@shipment_router.get("/shipments/{shipment_id}")
def get_shipment_by_id(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    return views.ShipmentService.get_shipment_by_id(shipment_id=shipment_id, db=db)


@shipment_router.patch("/update_shipment/{shipment_id}")
def patch_package(
    shipment_id: int,
    request: UpdateShipment = Body(...),
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return views.PackageService.update_package(shipment_id, request, db)



# =============================== PACKAGE =======================================


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
        limit=limit,
    )


@shipment_router.get("/packages/{package_id}", response_model=FetchPackage)
def get_package_by_id(
    package_id: int = Path(..., description="The ID of the package to retrieve"),
    db: Session = Depends(get_db),
):
    return views.PackageService.get_package_by_id(package_id, db)


@shipment_router.patch("/disable_package/{package_id}")
def disable_package(package_id: int, db: Session = Depends(get_db)):
    return views.PackageService.disable_package(package_id, db)


@shipment_router.patch("/update_package/{package_id}")
def patch_package(
    package_id: int,
    request: UpdatePackage = Body(...),
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return views.PackageService.update_package(package_id, request, db)


# =============================== CURRENCY =======================================


@shipment_router.post("/create_currency/")
def create_currency(request: CreateCurrency, db: Session = Depends(get_db)):
    return views.CurrencyService.create_currency(request, db)


@shipment_router.get("/currencies/", response_model=List[FetchCurrency])
def get_currencies(db: Session = Depends(get_db)):
    """Fetch all currencies."""
    return views.CurrencyService.get_currencies(db)


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
def get_currency_by_id(
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    """Fetch a single currency by ID."""
    return views.CurrencyService.get_currency_by_id(currency_id, db)
