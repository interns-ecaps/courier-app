# shipment/api/v1/models/status.py

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Table,
    Boolean,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import relationship, backref

from common.database import Base
from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

class ShipmentStatus(Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class StatusTracker(Base):
    __tablename__ = "status_tracker"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING)
    current_location = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    is_delivered = Column(Boolean, default=False)

    is_deleted = Column(Boolean, default=False)    

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    shipment = relationship("Shipment", back_populates="status")
    package = relationship("Package", back_populates="status")

    location = relationship("Address", back_populates="status")
