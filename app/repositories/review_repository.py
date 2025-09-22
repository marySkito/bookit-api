from sqlalchemy.orm import Session
from ..models.review import Review
from ..schemas.review import ReviewCreate

class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, review_data: ReviewCreate) -> Review:
        review = Review(**review_data.dict())
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_booking_id(self, booking_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.booking_id == booking_id).first()

    def get_service_reviews(self, service_id: int):
        return self.db.query(Review).join(Review.booking).filter(
            Review.booking.has(service_id=service_id)
        ).all()

    def update(self, review: Review, update_data: dict) -> Review:
        for field, value in update_data.items():
            if value is not None:
                setattr(review, field, value)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review: Review):
        self.db.delete(review)
        self.db.commit()