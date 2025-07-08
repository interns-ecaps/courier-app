# user/api/v1/models/users.py

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
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.declarative import declarative_base

from common.database import Base

# Base = declarative_base()


class UserType(str, Enum):
    IMPORTER_EXPORTER = "importer_exporter"
    SUPPLIER = "supplier"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    user_type = Column(
        SQLEnum(UserType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    sent_shipments = relationship(
        "Shipment", foreign_keys="[Shipment.sender_id]", back_populates="sender"
    )
    courier_shipments = relationship(
        "Shipment", back_populates="courier", foreign_keys="[Shipment.courier_id]"
    )

    packages = relationship(
        "Package", back_populates="user", foreign_keys="[Package.user_id]"
    )

    def __str__(self):
        return f"<User>-- {self.email}:{self.user_type}"
