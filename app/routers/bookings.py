from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..models.user import UserRole
from ..models.booking import BookingStatus
from ..schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from ..services.booking_service import BookingService

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    return booking_service.create_booking(booking_data, current_user.id)

@router.get("/", response_model=list[BookingResponse])
def get_bookings(
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    if current_user.role == UserRole.ADMIN:
        return booking_service.get_all_bookings(status_filter, from_date, to_date)
    else:
        return booking_service.get_user_bookings(current_user.id)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    booking = booking_service.get_booking_by_id(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return booking

@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    return booking_service.update_booking(booking_id, booking_data, current_user)

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    booking_service.delete_booking(booking_id, current_user)