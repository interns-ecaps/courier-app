#shipment/api/v1/models/package.py

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

# class IsNegotiable(Enum):
#     NO = "no"
#     YES = "yes"

class PackageType(Enum):
    STACKABLE_GOODS = "stackable_goods"
    NON_STACKABLE_GOODS = "non_stackable_goods"
    DANGEROUS_GOODS = "dangerous_goods"
    NON_DANGEROUS_GOODS = "non_dangerous_goods"
    DANGEROUS_STACKABLE_GOODS = "dangerous_stackable_goods"
    DANGEROUS_NON_STACKABLE_GOODS = "dangerous_non_stackable_goods"

class Currency(Base):
    __tablename__ = "currency"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(3), nullable=False)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    packages = relationship("Package", back_populates="currency")



class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, index=True)
    # shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    # tracking_number = Column(ForeignKey("shipments.tracking_number"), nullable=False)
    package_type = Column(SQLEnum(PackageType), default=PackageType.STACKABLE_GOODS)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)
    length = Column(Numeric(10, 2), nullable=False)
    width = Column(Numeric(10, 2), nullable=False)
    height = Column(Numeric(10, 2), nullable=False)
   
    # is_negotiable = Column(SQLEnum(IsNegotiable), default=IsNegotiable.NO)
    is_negotiable = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Pricing
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    final_cost = Column(Numeric(10, 2), nullable=True)

    # payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shipment = relationship("Shipment", back_populates="packages")
    user = relationship("User", back_populates="packages", foreign_keys=[user_id])
    payment = relationship("Payment", back_populates="package")
    currency = relationship("Currency", back_populates="packages")
    status = relationship("StatusTracker", back_populates="package")
