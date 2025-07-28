from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pymongo.collection import ReturnDocument
import secrets
import string
from datetime import datetime, timedelta

from database.config import user_collection
from models.user import Usercreate, UserInResponse, Userupdate, PasswordResetRequest, PasswordResetConfirm
from models.token import Token, TokenData
from utils.hashing import hash_password, verify_password
from utils.idincrement import increment_user_id
from core.auth import create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # Use absolute path here

# ──────────────────────────────────────────────
# Get current user from JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return TokenData(username=payload.get("sub"), role=payload.get("role", "user"))

# ──────────────────────────────────────────────
# Optional role-based access decorator
def role_required(required_role: str):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker

# ──────────────────────────────────────────────
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "user")}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ──────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    user = user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")
    
    # Generate reset token
    reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    
    # Store reset token in database
    user_collection.update_one(
        {"email": request.email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expiry": reset_token_expiry
        }}
    )
    
    # In a real application, you would send this token via email
    # For now, we'll return it in the response
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token,
        "expires_at": reset_token_expiry.isoformat()
    }

# ──────────────────────────────────────────────
@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    user = user_collection.find_one({
        "email": request.email,
        "reset_token": request.reset_token
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    # Check if token is expired
    if user.get("reset_token_expiry") and datetime.utcnow() > user["reset_token_expiry"]:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password and clear reset token
    hashed_password = hash_password(request.new_password)
    user_collection.update_one(
        {"email": request.email},
        {"$set": {"hashed_password": hashed_password}, "$unset": {"reset_token": "", "reset_token_expiry": ""}}
    )
    
    return {"message": "Password successfully reset"}

# ──────────────────────────────────────────────
@router.get("/users", response_model=list[UserInResponse])
async def get_users(current_user: TokenData = Depends(get_current_user)):
    users = user_collection.find({}, {"_id": 0})
    user_list = [UserInResponse(**user) for user in users]
    if not user_list:
        raise HTTPException(status_code=404, detail="No users found")
    return user_list

# ──────────────────────────────────────────────
@router.post("/user", response_model=UserInResponse)
async def create_user(user: Usercreate):
    if user_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user_id = increment_user_id()
    user_dict = user.model_dump()
    user_dict["id"] = new_user_id
    user_dict["hashed_password"] = hash_password(user.hashed_password)
    user_dict["created_at"] = datetime.utcnow()
    user_collection.insert_one(user_dict)
    return UserInResponse(**user_dict)

# ──────────────────────────────────────────────
@router.get("/users/{user_id}", response_model=UserInResponse)
async def get_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    user = user_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**user)

# ──────────────────────────────────────────────
@router.get("/profile", response_model=UserInResponse)
async def get_current_user_profile(current_user: TokenData = Depends(get_current_user)):
    user = user_collection.find_one({"username": current_user.username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**user)

# ──────────────────────────────────────────────
@router.put("/profile", response_model=UserInResponse)
async def update_profile(user: Userupdate, current_user: TokenData = Depends(get_current_user)):
    # Only allow users to update their own profile
    updated_user = user_collection.find_one_and_update(
        {"username": current_user.username},
        {"$set": user.model_dump(exclude_unset=True)},
        return_document=ReturnDocument.AFTER
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**updated_user)

# ──────────────────────────────────────────────
@router.put("/users/{user_id}", response_model=UserInResponse)
async def update_user(user_id: int, user: Userupdate, current_user: TokenData = Depends(role_required("admin"))):
    updated_user = user_collection.find_one_and_update(
        {"id": user_id},
        {"$set": user.model_dump(exclude_unset=True)},
        return_document=ReturnDocument.AFTER
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**updated_user)

# ──────────────────────────────────────────────
@router.put("/change-password")
async def change_password(new_password: str, current_user: TokenData = Depends(get_current_user)):
    hashed_password = hash_password(new_password)
    result = user_collection.update_one(
        {"username": current_user.username},
        {"$set": {"hashed_password": hashed_password}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password successfully changed"}

# ──────────────────────────────────────────────
@router.delete("/users/{user_id}", response_model=UserInResponse)
async def delete_user(user_id: int, current_user: TokenData = Depends(role_required("admin"))):
    deleted_user = user_collection.find_one_and_delete({"id": user_id}, projection={"_id": 0})
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInResponse(**deleted_user)
