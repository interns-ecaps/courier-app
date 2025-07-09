# shipment/api/v1/models/address.py


from datetime import datetime
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
    func,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from common.database import Base

# Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    addresses = relationship(
        "Address", back_populates="country", cascade="all, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(50))
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country_code = Column(Integer, ForeignKey("countries.id"), nullable=False)
    landmark = Column(String(255))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))

    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="addresses")

    pickup_shipments = relationship(
        "Shipment",
        foreign_keys="Shipment.pickup_address_id",
        back_populates="pickup_address",
    )

    country = relationship("Country", back_populates="addresses")

    # status = relationship("StatusTracker", back_populates="location")
