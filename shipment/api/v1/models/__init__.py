# shipment/api/v1/models/__init__.py

from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.models.package import Package
from shipment.api.v1.models.payment import Payment
from shipment.api.v1.models.status import StatusTracker
from shipment.api.v1.models.package import Currency
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
__all__ = ["Base", "Shipment", "Package", "Payment", "StatusTracker", "Currency"]
