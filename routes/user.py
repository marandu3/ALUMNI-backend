from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from database.config import user_collection
from models.user import Usercreate, UserInResponse, UserLogin, Userupdate
from utils.idincrement import increment_user_id
from pymongo.collection import ReturnDocument
from utils.hashing import hash_password, verify_password
from fastapi.security import OAuth2PasswordBearer
from core.auth import create_access_token, decode_access_token
from models.token import Token, TokenData 

router = APIRouter()
# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme))-> TokenData:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return TokenData(username=payload.get("sub"), role=payload.get("role", "user"))


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user.get("role", "user")
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def role_required(required_role: str):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker

@router.get("/users", response_model=list[UserInResponse])
async def get_users( current_user: TokenData = Depends(get_current_user)):
    users = user_collection.find({}, {"_id": 0})  # Correct projection to exclude MongoDB's _id
    user_list = [UserInResponse(**user) for user in users]  # Using list comprehension for cleaner code
    if not user_list:
        raise HTTPException(status_code=404, detail="No users found")
    return user_list
# Alternatively, you can use the commented-out code below if you prefer a more verbose approach  
    # user_list = []
    # for user in users:
    #     user_list.append(UserInResponse(**user))
    # if not user_list:
    #     raise HTTPException(status_code=404, detail="No users found")
    # return user_list

@router.post("/users", response_model = UserInResponse)
async def create_user(user: Usercreate):
    existing_user = user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Increment the user ID
    new_user_id = increment_user_id()
    user_dict = user.model_dump()
    user_dict["id"] = new_user_id  # Assign the new ID to the user
    user_dict["hashed_password"] = hash_password(user.hashed_password)  # Hash the password before storing
    user_collection.insert_one(user_dict)
    return UserInResponse(**user_dict)  # Return the user with the new ID

@router.get("/users/{user_id}", response_model=UserInResponse)
async def get_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    # You can fetch all users and then find the specific user, but it's not efficient
    # Uncomment the following lines if you want to fetch all users first
    # This is not recommended for performance reasons, especially with large datasets.
    # However, if you want to do it this way, you can use the following code:
    # #if you want to fetch all users and then find one user here is the code
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
    return UserInResponse(**user)

@router.put("/users/{user_id}", response_model=UserInResponse)
async def update_user(user_id: int, user: Userupdate, current_user: TokenData = Depends(get_current_user)):
    updated_user = user_collection.find_one_and_update(
        {"id": user_id},
        {"$set": user.model_dump()},
        return_document=ReturnDocument.AFTER  # returns the updated document
    )

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserInResponse(**updated_user)

#route to change password
@router.put("/users/{user_id}/change-password", response_model=UserInResponse)
async def change_password(user_id: int, new_password: str , current_user: TokenData = Depends(get_current_user)):
    user = user_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = hash_password(new_password)
    updated_user = user_collection.find_one_and_update(
        {"id": user_id},
        {"$set": {"hashed_password": hashed_password}},
        return_document=ReturnDocument.AFTER
    )
    
    return UserInResponse(**updated_user)

@router.delete("/users/{user_id}", response_model=UserInResponse)
async def delete_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    delete_user = user_collection.find_one_and_delete(
        {"id": user_id}, 
        {"_id": 0}
        )
    if not delete_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**delete_user)

