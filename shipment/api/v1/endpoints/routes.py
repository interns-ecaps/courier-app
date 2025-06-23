from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from common.database import get_db
from core.decorators.token_required import token_required
from shipment import views
from shipment.views import PaymentService
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    FetchCurrency,
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


@shipment_router.get("/currencies/", response_model=List[FetchCurrency])
def get_currency(db: Session = Depends(get_db)):
    # """Fetch all currencies."""
    return views.CurrencyService.get_currency(db)


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
    request: CreateCurrency = Body(...),
    db: Session = Depends(get_db),
):    
    return views.CurrencyService.replace_currency(currency_id, request, db) 


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
    user_id: Optional[int] = Query(default=None),
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
        user_id=user_id,
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
async def patch_shipment(
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
    return views.ShipmentService.update_shipment(shipment_id, request, db)


# @shipment_router.patch("/delete_shipment/{shipment_id}")
# def delete_shipment(shipment_id: int, db: Session = Depends(get_db)):
#     return views.ShipmentService.delete_shipment(shipment_id, db)


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
    return views.PackageService.get_package_by_id(package_id, db)


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

def update_payment(
    payment_id: int, request: UpdatePayment, db: Session = Depends(get_db)
):
    return PaymentService.update_payment(payment_id, request, db)


@shipment_router.patch("/disable_package/{package_id}")
@token_required
async def disable_package(
    request: Request, package_id: int, db: Session = Depends(get_db)
):
    return await views.PackageService.disable_package(package_id, db)
def disable_package(package_id: int, db: Session = Depends(get_db)):
    return views.PackageService.disable_package(package_id, db)
