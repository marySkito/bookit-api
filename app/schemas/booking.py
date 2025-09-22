from pydantic import BaseModel, validator
from datetime import datetime
from ..models.booking import BookingStatus

class BookingBase(BaseModel):
    service_id: int
    start_time: datetime

class BookingCreate(BookingBase):
    @validator('start_time')
    def start_time_must_be_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Start time must be in the future')
        return v

class BookingUpdate(BaseModel):
    start_time: datetime | None = None
    status: BookingStatus | None = None

class BookingResponse(BookingBase):
    id: int
    user_id: int
    end_time: datetime
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True