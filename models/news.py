from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewsCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    summary: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = []

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None

class NewsInResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = []
    author: str
    status: str = "published"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
