from pydantic import BaseModel, EmailStr
from datetime import date



class UserBase(BaseModel):
    email: EmailStr


class UserLogin(UserBase):
    password: str


class UserCreate(UserLogin):
    name: str


class User(UserBase):
    id: int
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    email: str


class BooksBase(BaseModel):
    name: str
    publisher: str
    author: str
    year_of_publication: date
    state_author: str


class CreateBooks(BooksBase):
    pass

class Books(CreateBooks):
    id: int
    class Config:
        from_attributes = True

class AddBookToUser(BaseModel):
    book_id: int