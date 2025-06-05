from fastapi import APIRouter, HTTPException, Depends
from models.news import NewsCreate, NewsUpdate, NewsInDB
from database.config import news_collection
from utils.idincrement import increment_news_id


router = APIRouter()



