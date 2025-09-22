from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime

class ServiceBase(BaseModel):
    title: str
    description: str | None = None
    price: Decimal
    duration_minutes: int
    is_active: bool = True

class ServiceCreate(ServiceBase):
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('duration_minutes')
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v

class ServiceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True