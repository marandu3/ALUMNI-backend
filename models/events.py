from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    location: str
    max_participants: Optional[int] = None
    category: str = "general"
    image_url: Optional[str] = None
    registration_deadline: Optional[datetime] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    status: Optional[str] = None

class EventRegistration(BaseModel):
    additional_info: Optional[str] = None

class EventInResponse(BaseModel):
    id: str
    title: str
    description: str
    event_date: datetime
    location: str
    max_participants: Optional[int] = None
    category: str
    image_url: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    created_by: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    registrations: List[dict] = [] 