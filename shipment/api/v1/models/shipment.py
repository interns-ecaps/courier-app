#shipment/api/v1/models/shipment.py

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
# from shipment.api.v1.models.payment import PaymentStatus

from common.database import Base
from sqlalchemy.ext.declarative import declarative_base

from shipment.api.v1.models.payment import PaymentStatus

# Base = declarative_base()
import ulid




class ShipmentType(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    SAME_DAY = "same_day"


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(
    String(40),
    unique=True,
    index=True,
    nullable=False,
    default=lambda: f"SHPMNT_{ulid.new()}"
)
    # Sender info
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_name = Column(String(100), nullable=False)
    sender_phone = Column(String(20), nullable=False)
    sender_email = Column(String(255))
    pickup_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)

    # Recipient info
    recipient_name = Column(String(100), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    recipient_email = Column(String(255))
    delivery_address_text = Column(Text, nullable=True)

    # Courier assignment
    courier_id = Column(Integer, ForeignKey("users.id"))

    # Shipment details
    shipment_type = Column(SQLEnum(ShipmentType), default=ShipmentType.STANDARD)
    # shipment_status_id = Column(Integer, ForeignKey("status_tracker.id"), nullable=False)

    # Package details
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    

    # Dates
    pickup_date = Column(DateTime(timezone=True))
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)

    # Additional info
    special_instructions = Column(Text)
    insurance_required = Column(Boolean, default=False)
    signature_required = Column(Boolean, default=False)

    # Payment details
    # payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    # payment_status = Column(String(100), ForeignKey("payments.payment_status"))
    
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    courier = relationship("User", back_populates="courier_shipments", foreign_keys=[courier_id])
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_shipments")

    pickup_address = relationship("Address", foreign_keys=[pickup_address_id], back_populates="pickup_shipments")
    # delivery_address = relationship("Address", foreign_keys=[delivery_address_id], back_populates="delivery_shipments")

    payment = relationship("Payment", back_populates="shipment")



    status = relationship("StatusTracker", back_populates="shipment")

    packages = relationship("Package", back_populates="shipment", cascade="all, delete-orphan", single_parent=True)
