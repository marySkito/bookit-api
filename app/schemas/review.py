from pydantic import BaseModel, validator
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int
    comment: str | None = None

    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewCreate(ReviewBase):
    booking_id: int

class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None

    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewResponse(ReviewBase):
    id: int
    booking_id: int
    created_at: datetime

    class Config:
        from_attributes = True