# app/main.py
from fastapi import FastAPI
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.services import router as services_router
from .routers.bookings import router as bookings_router

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/me", tags=["users"])
app.include_router(services_router, prefix="/services", tags=["services"])
app.include_router(bookings_router, prefix="/bookings", tags=["bookings"])

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to BookitAPI"}
