from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    graduatedyear: int | None = None
    phone: str | None = None
    role: str | None = None

    class Config:
        'userExample' == {
            "id": 1,
            "username": "johndoe",
            "email": "myemail@email.com",
            "full_name" : "John Doe",
            "phone": "+1234567890",
            "role": "alumni"
        }


class userInDB(User):
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


