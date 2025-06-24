from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import HTTPException, status

from passlib.context import CryptContext

from common.database import SessionLocal
from common.config import settings

from user.api.v1.utils.auth import create_access_token, create_refresh_token
from user.api.v1.models.users import User
from user.api.v1.schemas.user import (
    CreateCountry,
    CreateUser,
    SignUpRequest,
    UpdateCountry,
    UpdateUser,
)
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session
from fastapi import HTTPException




from user.api.v1.models.address import Address, Country
from user.api.v1.schemas.user import CreateAddress
from sqlalchemy.orm import Session


# user/views/address_service.py or similar
from fastapi import HTTPException
from sqlalchemy.orm import Session
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from user.api.v1.schemas.user import CreateAddress  # 👈 import your schema





# ========================== COUNTRY =========================


class CountryService:
    @staticmethod
    def create_country(country_data: CreateCountry, db: Session):
        name = country_data.name.strip()

        if not name:
            raise HTTPException(
                status_code=400, detail="Country name cannot be null or empty"
            )

        existing = (
            db.query(Country)
            .filter(
                func.lower(func.trim(Country.name)) == name.lower(),
                Country.is_deleted == False,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country = Country(name=name)
        db.add(country)
        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def get_all_countries(db: Session, page: int = 1, limit: int = 10):
        query = db.query(Country).filter(Country.is_deleted == False)
        total = query.count()
        countries = query.offset((page - 1) * limit).limit(limit).all()

        return {"page": page, "limit": limit, "total": total, "results": countries}

    @staticmethod
    def get_country_by_id(country_id: int, db: Session):
        country = (
            db.query(Country)
            .filter(Country.id == country_id, Country.is_deleted == False)
            .first()
        )

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        return country

    @staticmethod
    def update_country(country_id: int, country_data: UpdateCountry, db: Session):
        country = (
            db.query(Country)
            .filter(Country.id == country_id, Country.is_deleted == False)
            .first()
        )

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        # Handle soft delete
        if country_data.is_deleted is not None:
            country.is_deleted = country_data.is_deleted

        # Handle name update
        if country_data.name is not None:
            name = country_data.name.strip()
            if not name:
                raise HTTPException(
                    status_code=400, detail="Country name cannot be null or empty"
                )

            # Check for duplicates (exclude current)
            existing = (
                db.query(Country)
                .filter(
                    Country.id != country_id,
                    func.lower(func.trim(Country.name)) == name.lower(),
                    Country.is_deleted == False,
                )
                .first()
            )

            if existing:
                raise HTTPException(status_code=400, detail="Country already exists")

            country.name = name

        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def replace_country(country_id: int, new_data: CreateCountry, db: Session):
        country = (
            db.query(Country)
            .filter(Country.id == country_id, Country.is_deleted == False)
            .first()
        )

        if not country:
            raise HTTPException(status_code=404, detail="Country not found")

        name = new_data.name.strip()
        if not name:
            raise HTTPException(
                status_code=400, detail="Country name cannot be null or empty"
            )

        # Check for duplicates (exclude current)
        existing = (
            db.query(Country)
            .filter(
                Country.id != country_id,
                func.lower(func.trim(Country.name)) == name.lower(),
                Country.is_deleted == False,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Country already exists")

        country.name = name

        db.commit()
        db.refresh(country)
        return country
