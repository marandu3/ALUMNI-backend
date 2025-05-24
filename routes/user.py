from fastapi import APIRouter, HTTPException
from database.config import user_collection
from models.user import User

router = APIRouter()

@router.get("/users")
async def get_users():
    users = user_collection.find({}, {"_id": 0})  # Correct projection to exclude MongoDB's _id
    user_list = []
    for user in users:
        user_list.append(User(**user))
    if not user_list:
        raise HTTPException(status_code=404, detail="No users found")
    return user_list

@router.post("/users")
async def create_user(user: User):
    existing_user = user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_dict = user.model_dump()
    user_collection.insert_one(user_dict)
    return {"message": "User created successfully", "user": user_dict}

@router.get("/users/{user_id}")
async def get_user(user_id: int):

    ##if you want to fetch all users and then find one user here is the code
    # users = user_collection.find({}, {"_id": 0})  # Correct projection to exclude MongoDB's _id
    # user_list = []
    # for user in users:
    #     user_list.append(User(**user))
    
    # #finding a specific user by id
    # if user_id not in [user.id for user in user_list]:
    #     raise HTTPException(status_code=404, detail="User not found")
    # else:
    #     for user in user_list:
    #         if user.id == user_id:
    #             return user


    # Alternatively, you can directly query the database for a specific user
    user = user_collection.find_one({"id": user_id}, {"_id": 0})  # Only two arguments
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)
