from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class Usercreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: UserRole = UserRole.user
    hashed_password: str
    is_active: bool = True

class Userupdate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: UserRole = UserRole.user
    is_active: bool = True

class UserInDB(Usercreate):
    id: int

class UserInResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: UserRole | None = None
    is_active: bool = True
    is_superuser: bool = False

class UserLogin(BaseModel):
    username: str
    password: str
