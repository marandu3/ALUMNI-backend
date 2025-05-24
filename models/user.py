from pydantic import BaseModel, EmailStr

#this model is used as input and to see some of the user details
class Usercreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: str | None = None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

#this model is used as data stored in the db and it extends User
class UserInDB(Usercreate):
    id:int

#this model is used to return the user details in the response
class UserInResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: str | None = None
    is_active: bool = True
    is_superuser: bool = False
