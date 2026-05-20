from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.services import router as services_router
from .routers.bookings import router as bookings_router
from .routers.reviews import router as reviews_router
from .config import settings
from .database import engine, Base
from . import models
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

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-create test users on startup
@app.on_event("startup")
async def create_test_users():
    from .database import SessionLocal
    from .models.user import User, UserRole
    from .utils.auth import get_password_hash
    
    db = SessionLocal()
    try:
        # Create test regular user
        if not db.query(User).filter(User.email == "testuser@bookit.com").first():
            test_user = User(
                name="Test User",
                email="testuser@bookit.com",
                password_hash=get_password_hash("testpass123"),
                role=UserRole.USER
            )
            db.add(test_user)
        
        # Create test admin user
        if not db.query(User).filter(User.email == "admin@bookit.com").first():
            admin_user = User(
                name="Admin User",
                email="admin@bookit.com",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
        
        db.commit()
        print("✅ Test users created successfully")
    except Exception as e:
        print(f"⚠️ Error creating test users: {e}")
    finally:
        db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
