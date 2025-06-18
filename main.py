from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shipment.api.v1.endpoints import api_router as shipping_endpoint
from user.api.v1.endpoints import api_router as user_endpoint
from user.api.v1.utils.auth import get_current_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(shipping_endpoint, prefix="/shipment")
app.include_router(user_endpoint, prefix="/user")
