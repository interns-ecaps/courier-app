from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shipment.api.v1.endpoints import api_router as shipment_router
from user.api.v1.endpoints import api_router as user_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shipment_router, prefix="/shipment", tags=["shipment"])
app.include_router(user_router, prefix="/user", tags=["user"])
