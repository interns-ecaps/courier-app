from fastapi import APIRouter, Body, Depends, HTTPException, Query
from shipment import views
from fastapi import Request, Depends, Path
from sqlalchemy.orm import Session
from common.database import get_db
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    FetchPackage,
    UpdatePackage,
    CreateStatusTracker,
    UpdateStatusTracker,
)
from typing import Optional, List

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
def patch_shipment(
    shipment_id: int,
    request: UpdateShipment = Body(...),
    db: Session = Depends(get_db),
):
    return views.ShipmentService.update_shipment(shipment_id, request, db)


# @shipment_router.patch("/delete_shipment/{shipment_id}")
# def delete_shipment(shipment_id: int, db: Session = Depends(get_db)):
#     return views.ShipmentService.delete_shipment(shipment_id, db)


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


# ============================= STATUS TRACKER ===================================


@shipment_router.post("/create_status_tracker/")
def create_status_tracker(request: CreateStatusTracker, db: Session = Depends(get_db)):
    return views.StatusTrackerService.create_status_tracker(request, db)

@shipment_router.get("/status/")
def get_status(
    shipment_id: Optional[int] = Query(default=None),
    package_id: Optional[int] = Query(default=None),
    status: Optional[ShipmentStatus] = Query(default=None),
    is_delivered: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return views.StatusTrackerService.get_status(
        db=db,
        shipment_id=shipment_id,
        package_id=package_id,
        status=status,
        is_delivered=is_delivered,
        page=page,
        limit=limit,
    )

@shipment_router.get("/status/{status_id}")
def get_status_by_id(
    status_id: int,
    db: Session = Depends(get_db),
):
    return views.StatusTrackerService.get_status_by_id(status_id=status_id, db=db)


@shipment_router.patch("/update_status_tracker/{status_id}")
def update_status_tracker(
    status_id: int,
    request: UpdateStatusTracker = Body(...),
    db: Session = Depends(get_db),
):
    return views.StatusTrackerService.update_status_tracker(
        status_id=status_id, status_data=request, db=db
)

@shipment_router.patch("/delete_status/{status_id}")
def delete_shipment(status_id: int, db: Session = Depends(get_db)):
    return views.StatusTrackerService.delete_shipment(status_id, db)

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
