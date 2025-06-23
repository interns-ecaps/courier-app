from fastapi import HTTPException
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.models.shipment import Shipment
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage
from sqlalchemy.orm import Session
from typing import List, Optional
from shipment.api.v1.models.payment import Payment, PaymentMethod, PaymentStatus
from shipment.api.v1.schemas.shipment import CreatePayment, UpdatePayment




class CurrencyService:
    async def create_currency(currency_data: CreateCurrency, db: Session):
        currency = currency_data.currency
        if not currency:
            raise Exception("currency is required")
        currency_obj = Currency(currency=currency_data.currency)
        db.add(currency_obj)
        db.commit()
        db.refresh(currency_obj)
        return currency_obj
       
    
    async def update_currency(currency_id: int, new_data: CreateCurrency, db: Session):
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        if not new_data.currency or new_data.currency.strip() == "":
         raise HTTPException(status_code=400, detail="Currency value cannot be null or empty")
        currency.currency = new_data.currency
        db.commit()
        db.refresh(currency)
        return currency
    
    @staticmethod
    async def get_currency_by_id(currency_id: int, db: Session):
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Currency not found")
        return currency

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
        query = db.query(Package)

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

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": results
        }

    def get_package_by_id(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        return package
    
    
class PaymentService:
    @staticmethod
    async def create_payment(request: CreatePayment, db: Session):
        # Validate shipment
        shipment = db.query(Shipment).filter_by(id=request.shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        existing_payment = db.query(Payment).filter(
        Payment.shipment_id == request.shipment_id,
        Payment.payment_status == PaymentStatus.COMPLETED
        ).first()
        
        if existing_payment:
            raise HTTPException(status_code=400, detail="Payment already completed for this shipment")
        # Validate package
        # package = db.query(Package).filter_by(id=shipment.package_id).first()
        # if not package:
        #     raise HTTPException(status_code=404, detail="Package not found")

        payment = Payment(
            shipment_id=request.shipment_id,
            package_id=shipment.package_id,
            payment_method=request.payment_method,
            payment_status=request.payment_status,
            payment_date=request.payment_date
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    async def get_payment_by_id(payment_id: int, db: Session):
        payment = db.query(Payment).filter(Payment.id == payment_id, Payment.is_deleted == False).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    @staticmethod
    async def update_payment(payment_id: int, new_data: UpdatePayment, db: Session):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        if new_data.shipment_id is not None:
            payment.shipment_id = new_data.shipment_id
        if new_data.payment_method is not None:
            payment.payment_method = new_data.payment_method
        if new_data.payment_status is not None:
            payment.payment_status = new_data.payment_status
        if new_data.payment_date is not None:
            payment.payment_date = new_data.payment_date
        if new_data.is_deleted is not None:
            payment.is_deleted = new_data.is_deleted
        db.commit()
        db.refresh(payment)
        return payment

     
from shipment.api.v1.models.package import Currency, Package, PackageType
from shipment.api.v1.schemas.shipment import CreateCurrency, CreatePackage, UpdatePackage
from sqlalchemy.orm import Session
from typing import List, Optional



class PackageService:
    async def create_package(package_data: CreatePackage, db: Session):
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
    async def get_packages(
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

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "results": results
        }

    async def get_package_by_id(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        return package
        
    @staticmethod
    async def disable_package(package_id: int, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        
        if package.is_delete:
            raise HTTPException(status_code=400, detail="Package is already deleted")

        package.is_delete = True

        try:
            db.commit()
            db.refresh(package)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while deleting package: {str(e)}"
            )

        return package

    async def update_package(package_id: int, package_data: UpdatePackage, db: Session):
        package = db.query(Package).filter(Package.id == package_id).first()
        # print(user, "::user")

        if not package:
            raise HTTPException(status_code=404, detail="Package not found.")

        for field, value in package_data.dict(exclude_unset=True).items():
            setattr(package, field, value)

        try:
            db.commit()
            db.refresh(package)  # optional — to return the updated version
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error while updating package: {str(e)}"
            )
        return package