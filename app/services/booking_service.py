from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from ..repositories.booking_repository import BookingRepository
from ..repositories.service_repository import ServiceRepository
from ..models.user import UserRole
from ..models.booking import BookingStatus
from ..schemas.booking import BookingCreate, BookingUpdate

class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.service_repo = ServiceRepository(db)

    def create_booking(self, booking_data: BookingCreate, user_id: int):
        # Validate service exists and is active
        service = self.service_repo.get_by_id(booking_data.service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        if not service.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service is not active"
            )

        # Calculate end time
        end_time = booking_data.start_time + timedelta(minutes=service.duration_minutes)

        # Check for booking conflicts
        if self.booking_repo.check_booking_conflict(
            booking_data.service_id, booking_data.start_time, end_time
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking conflicts with existing booking"
            )

        return self.booking_repo.create(booking_data, user_id, end_time)

    def get_user_bookings(self, user_id: int):
        return self.booking_repo.get_user_bookings(user_id)

    def get_all_bookings(self, status: BookingStatus = None, 
                        from_date: datetime = None, to_date: datetime = None):
        return self.booking_repo.get_all_bookings(status, from_date, to_date)

    def get_booking_by_id(self, booking_id: int):
        return self.booking_repo.get_by_id(booking_id)

    def update_booking(self, booking_id: int, booking_data: BookingUpdate, current_user):
        booking = self.booking_repo.get_by_id(booking_id)
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

        update_data = booking_data.dict(exclude_unset=True)

        # Handle different update scenarios
        if current_user.role == UserRole.ADMIN:
            # Admin can update any field
            pass
        else:
            # Regular users have restrictions
            if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot modify booking in current status"
                )
            
            # Users can only reschedule or cancel
            if "status" in update_data and update_data["status"] not in [
                BookingStatus.CANCELLED
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Users can only cancel bookings"
                )

        # If rescheduling, check for conflicts
        if "start_time" in update_data:
            service = self.service_repo.get_by_id(booking.service_id)
            new_end_time = update_data["start_time"] + timedelta(minutes=service.duration_minutes)
            
            if self.booking_repo.check_booking_conflict(
                booking.service_id, update_data["start_time"], new_end_time, booking.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Booking conflicts with existing booking"
                )
            
            update_data["end_time"] = new_end_time

        return self.booking_repo.update(booking, update_data)

    def delete_booking(self, booking_id: int, current_user):
        booking = self.booking_repo.get_by_id(booking_id)
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

        # Users can only delete before start time
        if current_user.role != UserRole.ADMIN and booking.start_time <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete booking after start time"
            )

        self.booking_repo.delete(booking)