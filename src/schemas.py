from pydantic import BaseModel, EmailStr
from datetime import date



class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserLogin(UserBase):
    pass


class UserCreate(UserBase):
    password: str


class User(UserCreate):
    id: int
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    email: str = None


class BooksBase(BaseModel):
    name: str
    publisher: str
    author: str
    year_of_publication: date
    state_author: str


class CreateBooks(BooksBase):
    id: int

class Books(CreateBooks):
    class Config:
        from_attributes = True

class AddBookToUser(BaseModel):
    book_id: int