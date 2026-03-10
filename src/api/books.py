from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.templates import templates
from src.schemas import CreateBooks, AddBookToUser
from src.models import Books, Users
from src.dependency import get_current_user

router = APIRouter(prefix="/books")


@router.post("")
def add_book(
        request: Request,
        book_data: CreateBooks,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
):
    book = Books(
        name = book_data.name,
        author = book_data.author,
        year_of_publication = book_data.year_of_publication,
        state_author = book_data.state_author,
        publisher = book_data.publisher,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return templates.TemplateResponse("add_book.html", {"request" : request})


@router.get("/add")
async def add_books(
        request: Request,
        current_user: Users = Depends(get_current_user),
):
    context = {
        "request": request
    }
    return templates.TemplateResponse("add_book.html", context)


@router.get("", response_class=HTMLResponse)
async def all_books(
        request: Request,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    stmt = select(Books)
    result = db.execute(stmt)
    books = result.scalars().all()
    return templates.TemplateResponse("all_books.html", {"request": request, "books": books})


@router.post("/my")
async def add_book_to_user(
        request: Request,
        add_book_data: AddBookToUser,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    book = db.query(Books).filter(Books.id == add_book_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    current_user.books.append(book)
    db.commit()
    books = db.execute(select(Books)).scalars().all()
    return templates.TemplateResponse("all_books.html", {"request": request, "books": books})