from fastapi import (
    APIRouter,
)
from shipment import views
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from common.database import get_db
from shipment.api.v1.schemas.shipment import CreateCurrency

shipment_router = APIRouter()


@shipment_router.get("/health_check/")
def health_check():
    return {"status": "active", "message": "Shipment Service is up and running"}


# ================================ CURRENCY =====================================


@shipment_router.post("/create_currency/")
def create_currency(request: CreateCurrency, db: Session = Depends(get_db)):
    return views.CurrencyService.create_currency(request, db)


# ==============================================================================
