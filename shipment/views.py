from datetime import datetime
from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.status import ShipmentStatus, StatusTracker
from shipment.api.v1.models.shipment import Shipment

# from shipment.api.v1.endpoints.routes import
from shipment.api.v1.models.status import ShipmentStatus
from shipment.api.v1.models.shipment import Shipment, ShipmentType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    CreateShipment,
    CreateStatusTracker,
    FetchPackage,
    FetchShipment,
    FetchStatus,
    ReplacePackage,
    UpdateCurrency,
    UpdatePackage,
    UpdateShipment,
    UpdateStatusTracker,
)
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from user.api.v1.models.address import Address
from user.api.v1.models.users import User
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage
from sqlalchemy.orm import Session
from typing import List, Optional
from shipment.api.v1.models.payment import Payment, PaymentMethod, PaymentStatus
from shipment.api.v1.schemas.shipment import CreatePayment, UpdatePayment
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.schemas.shipment import (
    CreateCurrency,
    CreatePackage,
    UpdatePackage,
)
from sqlalchemy.orm import Session
from typing import List, Optional

# ======================== CURRENCY SERVICE =========================


#============SHIPMENT==============#



#===============PACKAGE===================
class PackageService:
    def create_package(package_data: CreatePackage, db: Session):
        # currency_id = package_data.currency_id
        currency = (
            db.query(Currency).filter(Currency.id == package_data.currency_id).first()
        )
        if not currency:
            raise HTTPException(status_code=400, detail="Currency not found")

        try:
            package_type_enum = PackageType(package_data.package_type)
        except ValueError:
            raise Exception(f"Invalid package_type: {package_data.package_type}")

        package_obj = Package(
            package_type=package_type_enum,
            weight=package_data.weight,
            length=package_data.length,
            width=package_data.width,
            height=package_data.height,
            is_negotiable=package_data.is_negotiable,
            currency=currency,
        )
        db.add(package_obj)
        db.commit()
        db.refresh(package_obj)
        return package_obj

    @staticmethod
    def get_packages(
        db: Session,
        package_type: Optional[str] = None,
        currency_id: Optional[int] = None,
        is_negotiable: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ):
        query = db.query(Package).filter(Package.is_deleted == False)

        if package_type:
            try:
                query = query.filter(Package.package_type == PackageType(package_type))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid package_type")

        if currency_id:
            query = query.filter(Package.currency_id == currency_id)

        if is_negotiable is not None:
            query = query.filter(Package.is_negotiable == is_negotiable)

        total = query.count()
        results = query.offset((page - 1) * limit).limit(limit).all()

        return {"page": page, "limit": limit, "total": total, "results": results}

    def get_package_by_id(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_deleted:
            raise HTTPException(status_code=403, detail="Package has been deleted")

        return package


    def update_package(package_id: int, data: UpdatePackage,db: Session):
        package = db.query(Package).filter(Package.id == package_id, Package.is_deleted == False).first()
        print(package, "::::package")
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        print(data, "::DAta")
        update_data = data.dict(exclude_unset=True, exclude_none=True) 

        for field, value in update_data.items():  
            setattr(package, field, value)
        print(package.weight, "::::package.weight")
        package.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(package)
        return package


    @staticmethod
    def replace_package(package_id: int, package_data: ReplacePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")

        if package.is_deleted:
            raise HTTPException(status_code=403, detail="Package has been deleted")

        for field, value in package_data.dict().items():
            setattr(package, field, value)

        db.commit()
        db.refresh(package)
        return FetchPackage.model_validate(package)

    

# ========================= STATUS TRACKER SERVICE =========================


# ========================= PAYMENT SERVICE =========================


