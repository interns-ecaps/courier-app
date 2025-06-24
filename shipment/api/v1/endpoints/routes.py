from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from common.database import get_db
from shipment import views
from shipment.views import PackageService, PaymentService
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




#==================================SHIPMENT========================================#




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
def update_package(
    package_id: int = Path(..., description="ID of the package to update"),
    payload: UpdatePackage =  Body(...),
    db: Session = Depends(get_db),
):
        print(payload, "::payload")
        return PackageService.update_package(package_id, payload, db)
@shipment_router.put("/packages/{package_id}", response_model=FetchPackage)
def replace_package_route(
    package_id: int,
    payload: CreatePackage,
    db: Session = Depends(get_db)
):
    return PackageService.replace_package(package_id, payload, db)




# ============================= STATUS TRACKER ===================================

#================================PAYMENT==========================================
