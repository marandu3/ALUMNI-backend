from fastapi import APIRouter, HTTPException, Depends
from models.news import NewsCreate, NewsUpdate
from database.config import news_collection
from utils.idincrement import increment_news_id


router = APIRouter()

#route to create new news
@router.post("/news", response_model=NewsCreate)
async def create_news(news: NewsCreate):
    news_dict = news.model_dump()
    # Insert the news item into the database
    result = news_collection.insert_one(news_dict)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create news item")
    
    return NewsCreate(**news_dict)