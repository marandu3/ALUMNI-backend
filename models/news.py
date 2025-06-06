from pydantic import BaseModel
from datetime import datetime

class NewsUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    # published_at: datetime.now | None   # Optional, defaults to None

class NewsCreate(BaseModel):
    title: str
    content: str
    # published_at: datetime.now | None   # Optional, defaults to None


class NewsInResponse(NewsCreate):
    author: str 
    
