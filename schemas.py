from pydantic import BaseModel, EmailStr
from datetime import date



class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    email: str = None

class Books(BaseModel):
    id: int
    name: str
    publisher: str
    author: str
    year_of_publication: date
    class Config:
        from_attributes = True

class AddBookToUser(BaseModel):
    book_id: int