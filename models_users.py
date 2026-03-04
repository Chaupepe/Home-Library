from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey, BLOB
from sqlalchemy.orm import relationship
from database import Base

user_book_association = Table(
    "user_book_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
)

class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    author = Column(String, unique = True, index=True, nullable=False)
    year_of_publication = Column(Date, nullable=False)
    state_author = Column(String, nullable=False)
    publisher = Column(String, nullable=False)

    users = relationship("Users", secondary= "user_book_association", back_populates="books")

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique = True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar = Column(BLOB, default=None)
    books = relationship("Books", secondary = "user_book_association", back_populates="users")
