from fastapi import APIRouter, Body, Depends, HTTPException, Query
from shipment import views
from fastapi import Request, Depends, Path
from sqlalchemy.orm import Session
from fastapi import Request
from common.database import get_db
from core.decorators.token_required import token_required
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    FetchPackage,
    CreatePayment,
    UpdatePayment,
    FetchPayment,
)
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    FetchPackage,
    UpdatePackage,
)
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    FetchPackage,
    UpdatePackage,
)
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    FetchPackage,
    UpdatePackage,
    CreateStatusTracker,
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
from shipment.views import PaymentService


# ================================ SHIPMENT =====================================


@shipment_router.post("/create_shipment/")
@token_required
async def create_shipment(request: Request,payload: CreateShipment, db: Session = Depends(get_db)):
    return await views.ShipmentService.create_shipment(payload, db)


@shipment_router.patch("/update_currency/{currency_id}")
@token_required
async def update_currency(
    request: Request,currency_id: int, payload: CreateCurrency, db: Session = Depends(get_db)
):
    return await views.CurrencyService.update_currency(currency_id, payload, db)


@shipment_router.get("/shipments/")
@token_required
async def get_shipments(
    request: Request,
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    shipment_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.get_shipments(
        db=db,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        shipment_type=shipment_type,
        page=page,
        limit=limit,
    )


@shipment_router.get("/shipments/{shipment_id}")
@token_required
async def get_shipment_by_id(
    request: Request,
    shipment_id: int,
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.get_shipment_by_id(shipment_id=shipment_id, db=db)


@shipment_router.patch("/update_shipment/{shipment_id}")
@token_required
async def patch_package(
    request: Request,
    shipment_id: int,
    payload: UpdateShipment = Body(...),
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return await views.PackageService.update_package(shipment_id, payload, db)


@shipment_router.patch("/delete_shipment/{shipment_id}")
@token_required
async def delete_shipment(request: Request,shipment_id: int, db: Session = Depends(get_db)):
    return await views.ShipmentService.delete_shipment(shipment_id, db)


# =============================== PACKAGE =======================================


@shipment_router.post("/create_package/")
@token_required
async def create_package(
    request_body: CreatePackage,  # your actual input schema
    request: Request,  # the raw HTTP request (for headers)
    db: Session = Depends(get_db),
):
    return await views.PackageService.create_package(request_body, db)


@shipment_router.get("/packages/")
@token_required
async def get_packages(
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.PackageService.get_packages(
        db=db,
        package_type=package_type,
        currency_id=currency_id,
        is_negotiable=is_negotiable,
        page=page,
        limit=limit,
    )


@shipment_router.get("/packages/{package_id}", response_model=FetchPackage)
@token_required
async def get_package_by_id(
    request: Request,
    package_id: int = Path(..., description="The ID of the package to retrieve"),
    db: Session = Depends(get_db),
):
    return await views.PackageService.get_package_by_id(package_id, db)


@shipment_router.patch("/update_package/{package_id}")
@token_required
async def patch_package(
    request: Request,
    package_id: int,
    payload: UpdatePackage = Body(...),
    db: Session = Depends(get_db),
):
    print(request.dict(exclude_unset=False))
    return await views.PackageService.update_package(package_id, payload, db)


# ============================= STATUS TRACKER ===================================


@shipment_router.post("/create_status_tracker/")
@token_required
async def create_status_tracker(
    request: Request,payload: CreateStatusTracker, db: Session = Depends(get_db)
):
    return await views.create_status_tracker(payload,db)


# =============================== CURRENCY =======================================


@shipment_router.post("/create_currency/")
@token_required
async def create_currency(
    request_body: CreateCurrency, request: Request, db: Session = Depends(get_db)
):
    return await views.CurrencyService.create_currency(request_body, db)


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
@token_required
async def get_currency_by_id(
    request: Request,
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.get_currency_by_id(currency_id, db)


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
@token_required
async def get_currency_by_id(
    request: Request,
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    """Fetch a single currency by ID."""
    return await views.CurrencyService.get_currency_by_id(currency_id, db)


# ==========payment=============


@shipment_router.post("/create_payment/", response_model=FetchPayment)
@token_required
async def create_payment(
    request: Request, payload: CreatePayment, db: Session = Depends(get_db)
):
    return await PaymentService.create_payment(payload, db)


@shipment_router.get("/get_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def get_payment(request: Request, payment_id: int, db: Session = Depends(get_db)):
    return await PaymentService.get_payment_by_id(payment_id, db)


@shipment_router.patch("/update_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def update_payment(
    request: Request,
    payment_id: int,
    payload: UpdatePayment,
    db: Session = Depends(get_db),
):
    return await PaymentService.update_payment(payment_id, payload, db)


@shipment_router.patch("/disable_package/{package_id}")
@token_required
async def disable_package(
    request: Request, package_id: int, db: Session = Depends(get_db)
):
    return await views.PackageService.disable_package(package_id, db)
