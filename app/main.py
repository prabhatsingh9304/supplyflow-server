import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.retailers import router as retailers_router
from app.api.v1.products import router as products_router
from app.api.v1.orders import router as orders_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.analytics import router as analytics_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SupplyFlow API",
    description="Supplier & Retailer Ordering Platform Backend",
    version="0.1.0",
)

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,https://supplyflow.waspx.ai",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(retailers_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(invoices_router)
app.include_router(analytics_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
