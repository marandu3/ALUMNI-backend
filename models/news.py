from pydantic import BaseModel
from datetime import datetime


class NewsCreate(BaseModel):
    title: str
    content: str
    author_id: int  # Assuming the author is a user with an ID
    # published_at: datetime.now | None   # Optional, defaults to None

class NewsUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    # published_at: datetime.now | None   # Optional, defaults to None

class NewsInDB(NewsCreate):
    id: int  # Unique identifier for the news item
    # created_at: datetime = datetime.now()  # Automatically set when the news is created