from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from ..models.booking import Booking, BookingStatus
from ..schemas.booking import BookingCreate

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, booking_data: BookingCreate, user_id: int, end_time: datetime) -> Booking:
        booking = Booking(
            user_id=user_id,
            service_id=booking_data.service_id,
            start_time=booking_data.start_time,
            end_time=end_time
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_by_id(self, booking_id: int) -> Booking | None:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def get_user_bookings(self, user_id: int):
        return self.db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_all_bookings(self, status: BookingStatus = None, 
                        from_date: datetime = None, to_date: datetime = None):
        query = self.db.query(Booking)
        
        if status:
            query = query.filter(Booking.status == status)
        if from_date:
            query = query.filter(Booking.start_time >= from_date)
        if to_date:
            query = query.filter(Booking.start_time <= to_date)
            
        return query.all()

    def check_booking_conflict(self, service_id: int, start_time: datetime, 
                             end_time: datetime, exclude_booking_id: int = None) -> bool:
        query = self.db.query(Booking).filter(
            and_(
                Booking.service_id == service_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                    and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                    and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
            
        return query.first() is not None

    def update(self, booking: Booking, update_data: dict) -> Booking:
        for field, value in update_data.items():
            if value is not None:
                setattr(booking, field, value)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def delete(self, booking: Booking):
        self.db.delete(booking)
        self.db.commit()