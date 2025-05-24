from fastapi import APIRouter, HTTPException, Depends
from database.config import user_collection
from models.user import User


router = APIRouter()

@router.get("/users")
async def get_users():
    users = user_collection.find()
    user_list = []
    for user in users:
        user_list.append(User(**user))
    return user_list
    