from fastapi import APIRouter
from .routes import shipment_router

api_router = APIRouter()
api_router.include_router(shipment_router, prefix="/v1", tags=["shipment"])

