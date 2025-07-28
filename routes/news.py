from fastapi import APIRouter, HTTPException, Depends
from models.news import NewsInResponse, NewsUpdate, NewsCreate
from database.config import news_collection
from routes.user import get_current_user, role_required
from models.token import Token, TokenData
from utils.idincrement import generate_news_id
from datetime import datetime
from typing import List

router = APIRouter()

#route to create new news (admin only)
@router.post("/news", response_model=NewsInResponse)
async def create_news(news: NewsCreate, current_user: TokenData = Depends(role_required("admin"))):
    news_dict = news.model_dump()
    news_dict["id"] = generate_news_id()
    news_dict["author"] = current_user.username
    news_dict["created_at"] = datetime.utcnow()
    news_dict["status"] = "published"

    # Insert the news item into the database
    result = news_collection.insert_one(news_dict)
    # Check if the insertion was successful
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create news item")
    
    # Get the created news with the generated ID
    created_news = news_collection.find_one({"_id": result.inserted_id}, {"_id": 0})
    return NewsInResponse(**created_news)

#route to retrieve all published news (public access)
@router.get("/news")
async def get_news():
    news = news_collection.find({"status": "published"}, {"_id": 0}).sort("created_at", -1)
    news_list = [NewsInResponse(**news_item) for news_item in news]
    if not news_list:
        raise HTTPException(status_code=404, detail="No news found")
    
    return news_list

#route to retrieve all news (admin only)
@router.get("/admin/news")
async def get_all_news(current_user: TokenData = Depends(role_required("admin"))):
    news = news_collection.find({}, {"_id": 0}).sort("created_at", -1)
    news_list = [NewsInResponse(**news_item) for news_item in news]
    if not news_list:
        raise HTTPException(status_code=404, detail="No news found")
    
    return news_list

#route to get news by category
@router.get("/news/category/{category}")
async def get_news_by_category(category: str):
    news = news_collection.find({"category": category, "status": "published"}, {"_id": 0}).sort("created_at", -1)
    news_list = [NewsInResponse(**news_item) for news_item in news]
    if not news_list:
        raise HTTPException(status_code=404, detail=f"No news found in category: {category}")
    
    return news_list

#route to get single news item
@router.get("/news/{news_id}")
async def get_news_by_id(news_id: str):
    news_item = news_collection.find_one({"id": news_id, "status": "published"}, {"_id": 0})
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    return NewsInResponse(**news_item)

#route to update news (admin only)
@router.put("/news/{news_id}", response_model=NewsInResponse)
async def update_news(news_id: str, news: NewsUpdate, current_user: TokenData = Depends(role_required("admin"))):
    news_dict = news.model_dump(exclude_unset=True)
    news_dict["updated_at"] = datetime.utcnow()
    
    updated_news = news_collection.find_one_and_update(
        {"id": news_id},
        {"$set": news_dict},
        return_document=True
    )
    if not updated_news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    return NewsInResponse(**updated_news)

#route to delete news from database (admin only)
@router.delete("/news/{news_id}", response_model=NewsInResponse)
async def delete_news(news_id: str, current_user: TokenData = Depends(role_required("admin"))):
    news_item = news_collection.find_one({"id": news_id}, {"_id": 0})
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")

    deleted_news = news_collection.find_one_and_delete({"id": news_id}, projection={"_id": 0})
    if not deleted_news:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsInResponse(**deleted_news)

#route to change news status (admin only)
@router.patch("/news/{news_id}/status")
async def change_news_status(news_id: str, status: str, current_user: TokenData = Depends(role_required("admin"))):
    if status not in ["draft", "published", "archived"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'draft', 'published', or 'archived'")
    
    result = news_collection.update_one(
        {"id": news_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="News item not found")
    
    return {"message": f"News status updated to {status}"}

#route to get news categories
@router.get("/news/categories")
async def get_news_categories():
    categories = news_collection.distinct("category")
    return {"categories": categories}