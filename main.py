from fastapi import FastAPI, HTTPException, Depends
from routes.user import router as user_router



app = FastAPI()
app.include_router(user_router , tags=["user"])
