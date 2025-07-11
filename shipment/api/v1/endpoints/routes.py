from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from razorpay import Client
import hmac
import hashlib
import json
from shipment.api.v1.models.payment import Payment, PaymentStatus


from common.database import get_db
from core.decorators.token_required import token_required
from shipment import views
from shipment.views import PackageService, PaymentService, StatusTrackerService, create_missing_status_trackers
from shipment.api.v1.models.status import StatusTracker, ShipmentStatus
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
from common.config import settings
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.models.shipment import ShipmentType
from shipment.api.v1.models.package import PackageType


shipment_router = APIRouter()


# =============================== CURRENCY =======================================


@shipment_router.post("/create_currency/", response_model=FetchCurrency)
@token_required
async def create_currency(request:Request,payload: CreateCurrency, db: Session = Depends(get_db)):
    return await views.CurrencyService.create_currency(request, payload, db)


@shipment_router.get("/currencies/")
@token_required
async def get_currencies(
    request:Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.get_currency(request, db=db, page=page, limit=limit)


@shipment_router.get("/currencies/{currency_id}", response_model=FetchCurrency)
@token_required
async def get_currency_by_id(
    request:Request,
    currency_id: int = Path(..., description="The ID of the currency to retrieve"),
    db: Session = Depends(get_db),
):
    # """Fetch a single currency by ID."""
    # return await views.CurrencyService.get_currency_by_id(currency_id, db)
    raise HTTPException(status_code=501, detail="get_currency_by_id not implemented")


@shipment_router.patch("/update_currency/{currency_id}", response_model=FetchCurrency)
@token_required
async def update_currency(
    request:Request,
    currency_id: int = Path(..., description="The ID of the currency to update"),
    payload: UpdateCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.update_currency(request, currency_id, payload, db)


@shipment_router.put("/replace_currency/{currency_id}", response_model=FetchCurrency)
@token_required
async def replace_currency(
    request:Request,
    currency_id: int = Path(..., description="The ID of the currency to update"),
    payload: ReplaceCurrency = Body(...),
    db: Session = Depends(get_db),
):
    return await views.CurrencyService.replace_currency(request, currency_id, payload, db)


# ================================ SHIPMENT =====================================

@shipment_router.get("/shipment_types/")
async def get_shipment_types():
    return {"shipment_types": [st.value for st in ShipmentType]}

@shipment_router.get("/package_types/")
async def get_package_types():
    return {"package_types": [pt.value for pt in PackageType]}

@shipment_router.post("/create_shipment/")
@token_required
async def create_shipment(request:Request,payload: CreateShipment, db: Session = Depends(get_db)):
    return await views.ShipmentService.create_shipment(request, payload, db)

@shipment_router.post("/shipments/{shipment_id}/accept_reject/")
@token_required
async def accept_reject_shipment(
    request: Request,
    shipment_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Endpoint for suppliers to accept or reject shipments"""
    action = payload.get("action")
    if not action:
        raise HTTPException(status_code=400, detail="Action is required")
    return await views.ShipmentService.accept_reject_shipment(request, shipment_id, action, db)


@shipment_router.get("/shipments/")
@token_required
async def get_shipments(
    request:Request,
    user_id: Optional[int] = Query(default=None),
    package_type: Optional[str] = Query(default=None),
    currency_id: Optional[int] = Query(default=None),
    courier_id: Optional[int] = Query(default=None),
    is_negotiable: Optional[bool] = Query(default=None),
    shipment_type: Optional[str] = Query(default=None),
    pickup_from: Optional[str] = Query(default=None),
    pickup_to: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    # Convert pickup_from and pickup_to to datetime if provided
    pickup_from_dt = None
    pickup_to_dt = None
    if pickup_from:
        try:
            pickup_from_dt = datetime.fromisoformat(pickup_from)
        except Exception:
            raise HTTPException(status_code=400, detail="pickup_from must be ISO datetime string")
    if pickup_to:
        try:
            pickup_to_dt = datetime.fromisoformat(pickup_to)
        except Exception:
            raise HTTPException(status_code=400, detail="pickup_to must be ISO datetime string")
    return await views.ShipmentService.get_shipments(
        request,
        db=db,
        user_id=user_id,
        package_type=package_type,
        currency_id=currency_id,
        courier_id=courier_id,
        is_negotiable=is_negotiable,
        shipment_type=shipment_type,
        pickup_from=pickup_from_dt,
        pickup_to=pickup_to_dt,
        page=page,
        limit=limit,
    )


@shipment_router.get("/shipments/{shipment_id}")
@token_required
async def get_shipment_by_id(
    request:Request,
    shipment_id: int,
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.get_shipment_by_id(request, shipment_id=shipment_id, db=db)


@shipment_router.patch("/update_shipment/{shipment_id}")
@token_required
async def patch_shipment(
    request:Request,
    shipment_id: int,
    payload: UpdateShipment = Body(...),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.update_shipment(request, shipment_id, payload, db)


@shipment_router.put("/replace_shipment/{shipment_id}")
@token_required
async def replace_shipment(
    request:Request,
    shipment_id: int,
    payload: ReplaceShipment = Body(...),
    db: Session = Depends(get_db),
):
    return await views.ShipmentService.replace_shipment(request, shipment_id, payload, db)


@shipment_router.post("/shipments/{shipment_id}/accept/")
@token_required
async def accept_shipment(request: Request, shipment_id: int, db: Session = Depends(get_db)):
    print("=== ACCEPT ENDPOINT REACHED ===")
    print(f"[DEBUG] Accept endpoint called for shipment_id={shipment_id}")
    status_tracker = db.query(StatusTracker).filter(StatusTracker.shipment_id == shipment_id).first()
    if not status_tracker:
        print(f"[DEBUG] No StatusTracker found for shipment_id={shipment_id}")
        raise HTTPException(status_code=404, detail="Status tracker not found for shipment")
    print(f"[DEBUG] Found StatusTracker id={status_tracker.id} for shipment_id={shipment_id}")
    try:
        # Use the enum value, not the name or uppercase string
        status_tracker.status = ShipmentStatus.ACCEPTED  # This will be 'accepted'
        db.commit()
        print(f"[DEBUG] Status updated to ACCEPTED for shipment_id={shipment_id}")
        return {"status": "accepted"}
    except Exception as e:
        print(f"[DEBUG] Exception while updating status: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update status: {e}")

@shipment_router.post("/shipments/{shipment_id}/reject")
@shipment_router.post("/shipments/{shipment_id}/reject/")
@token_required
async def reject_shipment(request: Request, shipment_id: int, db: Session = Depends(get_db)):
    status_tracker = db.query(StatusTracker).filter(StatusTracker.shipment_id == shipment_id).first()
    if not status_tracker:
        raise HTTPException(status_code=404, detail="Status tracker not found for shipment")
    status_tracker.status = ShipmentStatus.REJECTED
    db.commit()
    return {"status": "rejected"}


# ============================== PACKAGE =======================================


@shipment_router.post("/create_package/")
@token_required
async def create_package(request:Request,payload: CreatePackage, db: Session = Depends(get_db)):
    return await views.PackageService.create_package(request, payload, db)


@shipment_router.get("/packages/")
@token_required
async def get_packages(
    request:Request,
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


@shipment_router.get("/packages/{package_id}", response_model=FetchPackage)
@token_required
async def get_package_by_id(
    request:Request,
    package_id: int = Path(..., description="The ID of the package to retrieve"),
    db: Session = Depends(get_db),
):
    return await views.PackageService.get_package_by_id(request, package_id, db)


@shipment_router.patch("/update_package/{package_id}")
@token_required
async def update_package(
    request:Request,
    package_id: int = Path(..., description="ID of the package to update"),
    payload: UpdatePackage = Body(...),
    db: Session = Depends(get_db),
):
    print(payload, "::payload")
    return await PackageService.update_package(request, package_id, payload, db)


@shipment_router.put("/replace_package/{package_id}", response_model=FetchPackage)
@token_required
async def replace_package_route(
    request:Request,
    package_id: int, payload: ReplacePackage, db: Session = Depends(get_db)
):
    return await PackageService.replace_package(request,package_id, payload, db)


# ============================= STATUS TRACKER ===================================


@shipment_router.post("/create_status/", response_model=FetchStatus)
@token_required
async def create_status(request:Request,payload: CreateStatusTracker, db: Session = Depends(get_db)):
    return await StatusTrackerService.create_status_tracker(request, payload, db)


@shipment_router.get("/statuses/")
@token_required
async def get_statuses(
    request:Request,
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


@shipment_router.get("/statuses/{status_id}", response_model=FetchStatus)
@token_required
async def get_status_by_id(request:Request,status_id: int = Path(...), db: Session = Depends(get_db)):
    return await StatusTrackerService.get_status_by_id(request, status_id, db)


@shipment_router.patch("/update_status/{status_id}", response_model=FetchStatus)
@token_required
async def update_status(
    request:Request,status_id: int, payload: UpdateStatusTracker, db: Session = Depends(get_db)
):
    return await StatusTrackerService.update_status_tracker(request, status_id, payload, db)


@shipment_router.put("/replace_status/{status_id}", response_model=FetchStatus)
@token_required
async def replace_status(
    request:Request,status_id: int, payload: ReplaceStatus, db: Session = Depends(get_db)
):
    return await StatusTrackerService.replace_status_tracker(request, status_id, payload, db)


# ===========================PAYMENT=============


@shipment_router.post("/create_payment/", response_model=FetchPayment)
@token_required
async def create_payment(request:Request,payload: CreatePayment, db: Session = Depends(get_db)):
    return await PaymentService.create_payment(request, payload, db)


@shipment_router.get("/payments/")
@token_required
async def get_payments(
    request:Request,
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


@shipment_router.get("/payments/{payment_id}", response_model=FetchPayment)
@token_required
async def get_payment(request:Request,payment_id: int, db: Session = Depends(get_db)):
    return await PaymentService.get_payment_by_id(request,payment_id, db)


@shipment_router.patch("/update_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def update_payment(
    request:Request,payment_id: int, payload: UpdatePayment, db: Session = Depends(get_db)
):
    return await PaymentService.update_payment(request, payment_id, payload, db)


@shipment_router.put("/replace_payment/{payment_id}", response_model=FetchPayment)
@token_required
async def replace_payment(
    request:Request,payment_id: int, payload: ReplacePayment, db: Session = Depends(get_db)
):
    return await PaymentService.replace_payment(request, payment_id, payload, db)


# ===========================RAZORPAY PAYMENT=====================

@shipment_router.post("/razorpay/create-order")
@token_required
async def create_razorpay_order(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    amount = data.get("amount")
    currency = data.get("currency", "INR")
    shipment_id = data.get("shipment_id")
    package_id = data.get("package_id")

    if not amount or not shipment_id or not package_id:
        raise HTTPException(status_code=400, detail="Amount, shipment_id, and package_id are required")

    client = Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

    try:
        order = client.order.create({
            "amount": int(amount) * 100,  # Razorpay expects amount in paisa
            "currency": currency,
            "receipt": "receipt_id_1",
            "payment_capture": 1
        })

        # Create a payment record in your DB
        payment = Payment(
            shipment_id=shipment_id,
            package_id=package_id,
            payment_method="ONLINE",
            payment_status=PaymentStatus.PENDING,
            payment_date=datetime.now(timezone.utc),
            razorpay_order_id=order["id"]
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {"order_id": order["id"]}
    except Exception as e:
        print("Razorpay order creation error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@shipment_router.post("/razorpay/verify-payment")
@token_required
async def verify_razorpay_payment(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")

    client = Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        # --- FIX: Update payment record with razorpay_payment_id and set status to COMPLETED ---
        payment = db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()
        if payment:
            payment.razorpay_payment_id = razorpay_payment_id
            payment.payment_status = PaymentStatus.COMPLETED
            db.commit()
            print(f"Payment status updated to COMPLETED for payment_id={payment.id}")
        # --- END FIX ---
        return {"status": "success", "message": "Payment verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Payment verification failed: " + str(e))


@shipment_router.post("/razorpay/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    event = json.loads(body)
    event_type = event.get("event")
    payload = event.get("payload", {})

    print(f"Received webhook event: {event_type}")

    if event_type == "payment.captured":
        payment_entity = payload["payment"]["entity"]
        payment_id = payment_entity["id"]
        order_id = payment_entity["order_id"]
        print(f"Webhook: payment.captured for payment_id={payment_id}, order_id={order_id}")

        # Try to find payment by razorpay_payment_id
        payment = db.query(Payment).filter(Payment.razorpay_payment_id == payment_id).first()
        if not payment:
            print("No payment found by razorpay_payment_id, trying order_id...")
            payment = db.query(Payment).filter(Payment.razorpay_order_id == order_id).first()

        if payment:
            payment.payment_status = PaymentStatus.COMPLETED
            db.commit()
            print("Payment status updated to COMPLETED")
        else:
            print("No payment found for this payment_id or order_id")

    elif event_type == "payment.failed":
        payment_entity = payload["payment"]["entity"]
        payment_id = payment_entity["id"]
        order_id = payment_entity["order_id"]
        print(f"Webhook: payment.failed for payment_id={payment_id}, order_id={order_id}")

        payment = db.query(Payment).filter(Payment.razorpay_payment_id == payment_id).first()
        if not payment:
            print("No payment found by razorpay_payment_id, trying order_id...")
            payment = db.query(Payment).filter(Payment.razorpay_order_id == order_id).first()

        if payment:
            payment.payment_status = PaymentStatus.FAILED
            db.commit()
            print("Payment status updated to FAILED")
        else:
            print("No payment found for this payment_id or order_id")

    # Add more event types as needed

    return {"status": "ok"}


@shipment_router.post("/shipments/debug/create-missing-status-trackers")
@token_required
async def debug_create_missing_status_trackers(request: Request, db: Session = Depends(get_db)):
    create_missing_status_trackers(db)
    return {"status": "ok", "message": "Missing StatusTrackers created."}


@shipment_router.get("/shipments/{shipment_id}/status_id")
@token_required
async def get_shipment_status_id(
    request: Request,
    shipment_id: int,
    db: Session = Depends(get_db)
):
    """Get the status_id for a shipment, creating one if it doesn't exist"""
    from shipment.views import ensure_shipment_has_status_tracker
    
    # Check if shipment exists
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id, Shipment.is_deleted == False).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Get or create status tracker
    status_id = ensure_shipment_has_status_tracker(shipment_id, db)
    if not status_id:
        raise HTTPException(status_code=500, detail="Failed to get or create status tracker")
    
    return {"status_id": status_id, "shipment_id": shipment_id}


@shipment_router.get("/shipments/{shipment_id}/debug-payment")
@token_required
async def debug_shipment_payment(
    request: Request,
    shipment_id: int,
    db: Session = Depends(get_db)
):
    """Debug endpoint to check payment status for a shipment"""
    from shipment.api.v1.models.payment import Payment, PaymentStatus
    
    # Check if shipment exists
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id, Shipment.is_deleted == False).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Get payment for this shipment
    payment = (
        db.query(Payment)
        .filter(Payment.shipment_id == shipment_id, Payment.is_deleted == False)
        .first()
    )
    
    if not payment:
        return {
            "shipment_id": shipment_id,
            "payment_found": False,
            "payment_status": None,
            "expected_status": PaymentStatus.COMPLETED.value,
            "payment_completed": False
        }
    
    payment_completed = payment.payment_status == PaymentStatus.COMPLETED.value
    
    return {
        "shipment_id": shipment_id,
        "payment_found": True,
        "payment_id": payment.id,
        "payment_status": payment.payment_status,
        "expected_status": PaymentStatus.COMPLETED.value,
        "payment_completed": payment_completed,
        "razorpay_order_id": payment.razorpay_order_id,
        "razorpay_payment_id": payment.razorpay_payment_id
    }


