from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentRecord(BaseModel):
    name: str
    email: str
    phone: str
    amount: int
    purpose: str = Field(default="Alumni Payment")
    status: str
    order_id: str
    selcom_response: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
