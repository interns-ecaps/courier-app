from datetime import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from common.database import get_db
from core.decorators.token_required import token_required
from shipment import views
from shipment.views import PackageService, PaymentService, StatusTrackerService
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    FetchCurrency,
    FetchStatus,
    ReplaceCurrency,
    ReplacePackage,
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
@token_required
async def create_currency(
    request: Request, payload: CreateCurrency, db: Session = Depends(get_db)
):
    return await views.CurrencyService.create_currency(request, payload, db)


@shipment_router.get("/currencies/")
@token_required
async def get_currencies(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.get_currency(
        request, db=db, page=page, limit=limit
    )


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
@token_required
async def get_currency_by_id(
    request: Request,
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    # """Fetch a single currency by ID."""
    return await views.CurrencyService.get_currency_by_id(currency_id, db)


@shipment_router.patch("/update_currency/{currency_id}", response_model=FetchCurrency)
@token_required
async def update_currency(
    request: Request,
    currency_id: int = Path(..., description="The ID of the currency to update"),
    payload: UpdateCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.update_currency(
        request, currency_id, payload, db
    )


@shipment_router.put("/replace_currency/{currency_id}", response_model=FetchCurrency)
@token_required
async def replace_currency(
    request: Request,
    currency_id: int = Path(..., description="The ID of the currency to update"),
    payload: ReplaceCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.replace_currency(
        request, currency_id, payload, db
    )


# ================================ SHIPMENT =====================================


@shipment_router.post("/create_shipment/")
@token_required
async def create_shipment(
    request: Request, payload: CreateShipment, db: Session = Depends(get_db)
):
    return await views.ShipmentService.create_shipment(request, payload, db)


@shipment_router.get("/shipments/")
@token_required
async def get_shipments(
    request: Request,
    user_id: Optional[int] = Query(default=None),
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    shipment_type: Optional[str] = Query(default=None),
    pickup_from: Optional[str] = Query(default=None),
    pickup_to: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.get_shipments(
        request,
        db=db,
        user_id=user_id,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        shipment_type=shipment_type,
        pickup_from=pickup_from,
        pickup_to=pickup_to,
        page=page,
        limit=limit,
    )


# @shipment_router.get("/shipments/{shipment_id}")
# @token_required
# async def get_shipment_by_id(
#     request:Request,
#     shipment_id: int,
#     db: Session = Depends(get_db),
# ):
#     return await views.ShipmentService.get_shipment_by_id(shipment_id=shipment_id, db=db)


@shipment_router.patch("/update_shipment/{shipment_id}")
@token_required
async def patch_shipment(
    request: Request,
    shipment_id: int,
    payload: UpdateShipment = Body(...),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.update_shipment(
        request, shipment_id, payload, db
    )


@shipment_router.put("/replace_shipment/{shipment_id}")
@token_required
async def replace_shipment(
    request: Request,
    shipment_id: int,
    payload: ReplaceShipment = Body(...),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.replace_shipment(
        request, shipment_id, payload, db
    )


# ============================== PACKAGE =======================================


@shipment_router.post("/create_package/")
@token_required
async def create_package(
    request: Request, payload: CreatePackage, db: Session = Depends(get_db)
):
    return await views.PackageService.create_package(request, payload, db)


@shipment_router.get("/packages/")
@token_required
async def get_packages(
    request: Request,
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.PackageService.get_packages(
        request,
        db=db,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        page=page,
        limit=limit,
    )


# @shipment_router.get("/packages/{package_id}", response_model=FetchPackage)
# @token_required
# async def get_package_by_id(
#     request:Request,
#     package_id: int = Path(..., description="The ID of the package to retrieve"),
#     db: Session = Depends(get_db),
# ):
#     return await views.PackageService.get_package_by_id(package_id, db)


@shipment_router.patch("/update_package/{package_id}")
@token_required
async def update_package(
    request: Request,
    package_id: int = Path(..., description="ID of the package to update"),
    payload: UpdatePackage = Body(...),
    db: Session = Depends(get_db),
):
    print(payload, "::payload")
    return await PackageService.update_package(request, package_id, payload, db)


@shipment_router.put("/packages/{package_id}", response_model=FetchPackage)
@token_required
async def replace_package_route(
    request: Request,
    package_id: int,
    payload: ReplacePackage,
    db: Session = Depends(get_db),
):
    return await PackageService.replace_package(request, package_id, payload, db)


# ============================= STATUS TRACKER ===================================


@shipment_router.post("/create_status/", response_model=FetchStatus)
@token_required
async def create_status(
    request: Request, payload: CreateStatusTracker, db: Session = Depends(get_db)
):
    return await StatusTrackerService.create_status_tracker(request, payload, db)


@shipment_router.get("/statuses/")
@token_required
async def get_statuses(
    request: Request,
    shipment_id: Optional[int] = Query(default=None),
    package_id: Optional[int] = Query(default=None),
    status: Optional[ShipmentStatus] = Query(default=None),
    is_delivered: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await StatusTrackerService.get_status(
        request,
        db=db,
        shipment_id=shipment_id,
        package_id=package_id,
        status=status,
        is_delivered=is_delivered,
        page=page,
        limit=limit,
    )


# @shipment_router.get("/get_status/{status_id}", response_model=FetchStatus)
# @token_required
# async def get_status_by_id(request:Request,status_id: int = Path(...), db: Session = Depends(get_db)):
#     return await StatusTrackerService.get_status_by_id(status_id, db)


@shipment_router.patch("/update_status/{status_id}", response_model=FetchStatus)
@token_required
async def update_status(
    request: Request,
    status_id: int,
    payload: UpdateStatusTracker,
    db: Session = Depends(get_db),
):
    return await StatusTrackerService.update_status_tracker(
        request, status_id, payload, db
    )


@shipment_router.put("/replace_status/{status_id}", response_model=FetchStatus)
@token_required
async def replace_status(
    request: Request,
    status_id: int,
    payload: ReplaceStatus,
    db: Session = Depends(get_db),
):
    return await StatusTrackerService.replace_status_tracker(
        request, status_id, payload, db
    )


# ===========================PAYMENT=============


@shipment_router.post("/create_payment/", response_model=FetchPayment)
@token_required
async def create_payment(
    request: Request, payload: CreatePayment, db: Session = Depends(get_db)
):
    return await PaymentService.create_payment(request, payload, db)


@shipment_router.get("/payments/")
@token_required
async def get_payments(
    request: Request,
    shipment_id: Optional[int] = Query(default=None),
    package_id: Optional[int] = Query(default=None),
    payment_method: Optional[str] = Query(default=None),
    payment_status: Optional[str] = Query(default=None),
    payment_date: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.PaymentService.get_payments(
        request,
        db=db,
        shipment_id=shipment_id,
        package_id=package_id,
        payment_method=payment_method,
        payment_status=payment_status,
        payment_date=payment_date,
        page=page,
        limit=limit,
    )


# @shipment_router.get("/get_payment/{payment_id}", response_model=FetchPayment)
# @token_required
# async def get_payment(request:Request,payment_id: int, db: Session = Depends(get_db)):
#     return await PaymentService.get_payment_by_id(request,payment_id, db)


@shipment_router.patch("/update_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def update_payment(
    request: Request,
    payment_id: int,
    payload: UpdatePayment,
    db: Session = Depends(get_db),
):
    return await PaymentService.update_payment(request, payment_id, payload, db)


@shipment_router.put("/replace_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def replace_payment(
    request: Request,
    payment_id: int,
    payload: ReplacePayment,
    db: Session = Depends(get_db),
):
    return await PaymentService.replace_payment(request, payment_id, payload, db)
