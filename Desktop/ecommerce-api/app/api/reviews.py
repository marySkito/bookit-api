from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import Review, Product, User
from app.schemas.schemas import ReviewCreate, ReviewResponse
from app.core.security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        user_id = verify_token(credentials.credentials)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        Review.user_id == user.id,
        Review.product_id == review_data.product_id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You already reviewed this product")
    
    # Create review
    review = Review(
        user_id=user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=user.full_name,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    )

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).all()
    
    return [
        ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.user.full_name,
            product_id=review.product_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )
        for review in reviews
    ]

@router.get("/user", response_model=List[ReviewResponse])
async def get_user_reviews(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    reviews = db.query(Review).filter(
        Review.user_id == user.id
    ).order_by(Review.created_at.desc()).all()
    
    return [
        ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=user.full_name,
            product_id=review.product_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )
        for review in reviews
    ]

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(review)
    db.commit()