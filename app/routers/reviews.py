from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..models.user import UserRole
from ..schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from ..services.review_service import ReviewService

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    return review_service.create_review(review_data, current_user.id)

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review_service = ReviewService(db)
    review = review_service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review

@router.patch("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    return review_service.update_review(review_id, review_data, current_user)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    review_service.delete_review(review_id, current_user)

# Additional route for getting service reviews
@router.get("/services/{service_id}/reviews", response_model=list[ReviewResponse])
def get_service_reviews(service_id: int, db: Session = Depends(get_db)):
    review_service = ReviewService(db)
    return review_service.get_service_reviews(service_id)