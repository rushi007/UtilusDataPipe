from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

class CustomerModel(BaseModel):
    customer_id: str = Field(..., description="Unique customer ID")
    signup_date: date
    country: Optional[str] = None

class SubscriptionModel(BaseModel):
    customer_id: str = Field(..., description="Unique customer ID")
    start_date: date
    end_date: Optional[date] = None
    plan: str
    monthly_price: int = Field(..., ge=0)

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        if v and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("end_date cannot be before start_date")
        return v