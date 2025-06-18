# user/api/v1/models/__init__.py



from user.api.v1.models.users import User
from user.api.v1.models.address import Address
from user.api.v1.models.address import Country
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
__all__ = ["Base", "User", "Address", "Country"]
