from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.utils.auth import get_password_hash
from app.database import get_db

router = APIRouter()

@router.post("/users/create-admin")
def create_admin_user(
    name: str, 
    email: str, 
    password: str, 
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    
    # Check if user exists
    if user_repo.get_by_email(email):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create UserCreate schema
    user_data = UserCreate(name=name, email=email, password=password)
    
    # Hash password
    password_hash = get_password_hash(password)
    
    # Create user
    user = user_repo.create(user_data, password_hash)
    
    # Update to admin role
    user.role = UserRole.ADMIN
    db.commit()
    
    return {
        "msg": "Admin user created",
        "email": email,
        "role": "admin"
    }
       