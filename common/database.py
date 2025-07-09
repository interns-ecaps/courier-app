from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy import (
    create_engine,
)  # This function is used to create a connection to your database.
from sqlalchemy.orm import (
    sessionmaker,
)  # used to create a session factory, which will be responsible for creating new database sessions.
from sqlalchemy.ext.declarative import (
    declarative_base,
)  # used to create a base class for your models. Any class that inherits from this base class will be treated as a table in your database.
from common.config import settings
from sqlalchemy.orm import Session


DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
print(DATABASE_URL, "::::DATABASE_URL")
engine = create_engine(DATABASE_URL)  # responsile for connection pool to your database

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
