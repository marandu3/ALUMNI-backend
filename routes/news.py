from fastapi import APIRouter, HTTPException, Depends
from models.news import NewsInResponse, NewsUpdate, NewsCreate
from database.config import news_collection
from routes.user import get_current_user, login_for_access_token
from models.token import Token, TokenData


router = APIRouter()

#route to create new news
@router.post("/news", response_model=NewsInResponse)
async def create_news(news: NewsCreate, current_user: TokenData = Depends(get_current_user)):
    news_dict = news.model_dump()
    #decoding username from token
    news_dict["author"] = current_user.username

    # Insert the news item into the database
    result = news_collection.insert_one(news_dict)
    # Check if the insertion was successful
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create news item")
    
    return NewsInResponse(**news_dict)

#route to retrieve all news from database
@router.get("/news")
async def get_news(current_user: TokenData = Depends(get_current_user)):
    news = news_collection.find({}, {"_id":0})
    news_list = [NewsInResponse(**news) for news in news]
    if not news_list:
        raise HTTPException(status_code=404, detail="no news found")
    
    return news_list

#route to delete news from database
@router.delete("/news/{title}", response_model=NewsInResponse)
async def delete_user(title: str, current_user: TokenData = Depends(get_current_user)):
    news_item = news_collection.find_one({"title": title}, {"_id": 0})
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    if news_item["author"] != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this news")

    delete_news = news_collection.find_one_and_delete(
        {"title": title}, 
        {"_id": 0}
        )
    if not delete_user:
        raise HTTPException(status_code=404, detail="news not found")
    return NewsInResponse(**delete_news)