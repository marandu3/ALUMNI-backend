from fastapi import FastAPI, HTTPException, Depends
from routes.user import router as user_router
from routes.news import router as news_router




app = FastAPI()
app.include_router(user_router , tags=["user"])
app.include_router(news_router, tags=["news"])
