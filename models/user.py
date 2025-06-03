from pydantic import BaseModel, EmailStr
from enum import Enum

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
    role: UserRole = UserRole.user  # default is 'user', type is enum
    hashed_password: str
    is_active: bool = True

class Userupdate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: UserRole = UserRole.user  # restrict to only valid roles
    is_active: bool = True

# This model is used as data stored in the db and it extends Usercreate
class UserInDB(Usercreate):
    id: int

# This model is used to return the user details in the response
class UserInResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: UserRole | None = None  # optional in the response
    is_active: bool = True
    is_superuser: bool = False

class UserLogin(BaseModel):
    username: str
    password: str
