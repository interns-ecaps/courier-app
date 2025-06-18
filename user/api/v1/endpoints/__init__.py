from fastapi import APIRouter
from .routes import user_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/v1", tags=["user"])
