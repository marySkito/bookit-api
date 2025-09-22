from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repositories.review_repository import ReviewRepository
from ..repositories.booking_repository import BookingRepository
from ..models.user import UserRole
from ..models.booking import BookingStatus
from ..schemas.review import ReviewCreate, ReviewUpdate

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.booking_repo = BookingRepository(db)

    def create_review(self, review_data: ReviewCreate, user_id: int):
        # Validate booking exists and belongs to user
        booking = self.booking_repo.get_by_id(review_data.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        # Check if booking is completed
        if booking.status != BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings"
            )

        # Check if review already exists
        existing_review = self.review_repo.get_by_booking_id(review_data.booking_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this booking"
            )

        return self.review_repo.create(review_data)

    def get_review_by_id(self, review_id: int):
        return self.review_repo.get_by_id(review_id)

    def get_service_reviews(self, service_id: int):
        return self.review_repo.get_service_reviews(service_id)

    def update_review(self, review_id: int, review_data: ReviewUpdate, current_user):
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check permissions - only review owner can update
        if review.booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        update_data = review_data.dict(exclude_unset=True)
        return self.review_repo.update(review, update_data)

    def delete_review(self, review_id: int, current_user):
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check permissions - review owner or admin
        if (current_user.role != UserRole.ADMIN and 
            review.booking.user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        self.review_repo.delete(review)