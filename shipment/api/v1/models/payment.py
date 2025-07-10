#shipment/api/v1/models/payment.py

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

class PaymentMethod(Enum):
    CASH = "CASH"
    ONLINE = "ONLINE"
    WIRE_TRANSFER = "WIRE_TRANSFER"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    
    package_id = Column(ForeignKey("packages.id"), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime(timezone=True))

    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)

    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationship
    # payment = relationship("Shipment", back_populates="shipment")
    shipment = relationship("Shipment", back_populates="payment")

    # currency_id = relationship("Currency", back_populates="currency_id")

    package = relationship("Package", back_populates="payment")


