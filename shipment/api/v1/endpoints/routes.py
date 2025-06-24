from datetime import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from common.database import get_db
from shipment import views
from shipment.views import PaymentService, StatusTrackerService
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    FetchCurrency,
    FetchStatus,
    ReplaceCurrency,
    ReplacePayment,
    ReplaceShipment,
    ReplaceStatus,
    UpdateCurrency,
    CreatePackage,
    FetchPackage,
    UpdatePackage,
    CreateShipment,
    UpdateShipment,
    CreateStatusTracker,
    UpdateStatusTracker,
    CreatePayment,
    FetchPayment,
    UpdatePayment,
)


shipment_router = APIRouter()


# =============================== CURRENCY =======================================


@shipment_router.post("/create_currency/", response_model=FetchCurrency)
def create_currency(request: CreateCurrency, db: Session = Depends(get_db)):
    return views.CurrencyService.create_currency(request, db)


@shipment_router.get("/currencies/")
def get_currencies(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return views.CurrencyService.get_currency(db=db, page=page, limit=limit)


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
def get_currency_by_id(
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    # """Fetch a single currency by ID."""
    return views.CurrencyService.get_currency_by_id(currency_id, db)


@shipment_router.patch("/update_currency/{currency_id}", response_model=FetchCurrency)
def update_currency(
    currency_id: int = Path(..., description="The ID of the currency to update"),
    request: UpdateCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return views.CurrencyService.update_currency(currency_id, request, db)


@shipment_router.put("/replace_currency/{currency_id}", response_model=FetchCurrency)
def replace_currency(
    currency_id: int = Path(..., description="The ID of the currency to update"),
    request: ReplaceCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return views.CurrencyService.replace_currency(currency_id, request, db)


# ================================ SHIPMENT =====================================


@shipment_router.post("/create_shipment/")
def create_shipment(request: CreateShipment, db: Session = Depends(get_db)):
    return views.ShipmentService.create_shipment(request, db)


@shipment_router.get("/shipments/")
def get_shipments(
    user_id: Optional[int] = Query(default=None),
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
        user_id=user_id,
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


@shipment_router.put("/replace_shipment/{shipment_id}")
def replace_shipment(
    shipment_id: int,
    request: ReplaceShipment = Body(...),
    db: Session = Depends(get_db),
):
    return views.ShipmentService.replace_shipment(shipment_id, request, db)


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


@shipment_router.patch("/update_package/{package_id}")
def patch_package(
    package_id: int,
    request: UpdatePackage = Body(...),
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return views.PackageService.update_package(package_id, request, db)


# ============================= STATUS TRACKER ===================================


@shipment_router.post("/create_status/", response_model=FetchStatus)
def create_status(request: CreateStatusTracker, db: Session = Depends(get_db)):
    return StatusTrackerService.create_status_tracker(request, db)


@shipment_router.get("/statuses/")
def get_statuses(
    shipment_id: Optional[int] = Query(default=None),
    package_id: Optional[int] = Query(default=None),
    status: Optional[ShipmentStatus] = Query(default=None),
    is_delivered: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return StatusTrackerService.get_status(
        db=db,
        shipment_id=shipment_id,
        package_id=package_id,
        status=status,
        is_delivered=is_delivered,
        page=page,
        limit=limit,
    )


@shipment_router.get("/get_status/{status_id}", response_model=FetchStatus)
def get_status_by_id(status_id: int = Path(...), db: Session = Depends(get_db)):
    return StatusTrackerService.get_status_by_id(status_id, db)


@shipment_router.patch("/update_status/{status_id}", response_model=FetchStatus)
def update_status(
    status_id: int, request: UpdateStatusTracker, db: Session = Depends(get_db)
):
    return StatusTrackerService.update_status_tracker(status_id, request, db)


@shipment_router.put("/replace_status/{status_id}", response_model=FetchStatus)
def replace_status(
    status_id: int, request: ReplaceStatus, db: Session = Depends(get_db)
):
    return StatusTrackerService.replace_status_tracker(status_id, request, db)


# ===========================PAYMENT=============


@shipment_router.post("/create_payment/", response_model=FetchPayment)
def create_payment(request: CreatePayment, db: Session = Depends(get_db)):
    return PaymentService.create_payment(request, db)


@shipment_router.get("/payments/")
def get_payments(
    shipment_id: Optional[int] = Query(default=None),
    package_id: Optional[int] = Query(default=None),
    payment_method: Optional[str] = Query(default=None),
    payment_status: Optional[str] = Query(default=None),
    payment_date: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return views.PaymentService.get_payments(
        db=db,
        shipment_id=shipment_id,
        package_id=package_id,
        payment_method=payment_method,
        payment_status=payment_status,
        payment_date=payment_date,
        page=page,
        limit=limit,
    )


@shipment_router.get("/get_payment/{payment_id}", response_model=FetchPayment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return PaymentService.get_payment_by_id(payment_id, db)


@shipment_router.patch("/update_payment/{payment_id}", response_model=FetchPayment)
def update_payment(
    payment_id: int, request: UpdatePayment, db: Session = Depends(get_db)
):
    return PaymentService.update_payment(payment_id, request, db)


@shipment_router.put("/replace_payment/{payment_id}", response_model=FetchPayment)
def replace_payment(
    payment_id: int, request: ReplacePayment, db: Session = Depends(get_db)
):
    return PaymentService.replace_payment(payment_id, request, db)
