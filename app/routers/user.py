from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.user import UserResponse, UserUpdate
from ..services.user_service import UserService

router = APIRouter()

@router.get("/", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    return current_user

@router.patch("/", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.update_user(current_user, user_data)