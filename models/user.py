from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional

# Enum to restrict roles to 'admin' or 'user'
class UserRole(str, Enum):
    admin = "admin"
    user = "user"

# This model is used as input and to see some of the user details
class Usercreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    occupation: str | None = None
    company: str | None = None
    location: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.user  # default is 'user', type is enum
    hashed_password: str
    is_active: bool = True

class Userupdate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    occupation: str | None = None
    company: str | None = None
    location: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.user  # restrict to only valid roles
    is_active: bool = True

# This model is used as data stored in the db and it extends Usercreate
class UserInDB(Usercreate):
    id: int
    created_at: datetime

# This model is used to return the user details in the response
class UserInResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    occupation: str | None = None
    company: str | None = None
    location: str | None = None
    bio: str | None = None
    role: UserRole | None = None  # optional in the response
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
