from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.auth import router as auth_router
from app.routers.users import router as users_router
from .routers.services import router as services_router
from .routers.bookings import router as bookings_router
from .routers.reviews import router as reviews_router
from .config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="BookIt API",
    description="A production-ready REST API for a simple bookings platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/me", tags=["users"])
app.include_router(services_router, prefix="/services", tags=["services"])
app.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
app.include_router(reviews_router, prefix="/reviews", tags=["reviews"])

@app.get("/")
async def root():
    return {"message": "Welcome to BookIt API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
