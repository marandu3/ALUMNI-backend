from fastapi import APIRouter, HTTPException, Depends
from models.news import News, NewsInResponse
from database.config import news_collection
from utils.idincrement import increment_news_id


router = APIRouter()



