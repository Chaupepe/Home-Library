from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_db
from src.security import decode_access_token, verify_token
from src.templates import templates, credentials_exception
from src.schemas import CreateBooks, AddBookToUser
from src.models import Books, Users

router = APIRouter()


@router.post("/root/profile/add_book")
def add_book(
        request: Request,
        book_data: CreateBooks,
        db: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
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


@router.get("/root/profile/add_book")
async def add_books(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    context = {
        "request": request
    }
    return templates.TemplateResponse("add_book.html", context)


@router.get("/root/profile/all_books", response_class=HTMLResponse)
async def all_books(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")

    stmt = select(Books)
    result = db.execute(stmt)
    books = result.scalars().all()
    return templates.TemplateResponse("all_books.html", {"request": request, "books": books})


@router.post("/root/profile/all_books")
async def add_book_to_user(
        request: Request,
        add_book_data: AddBookToUser,
        db: Session = Depends(get_db),

):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    payload = decode_access_token(token)
    user = db.query(Users).filter(Users.email == payload["sub"]).first()
    book = db.query(Books).filter(Books.id == add_book_data.book_id).first()
    user.books.append(book)
    db.commit()
    return templates.TemplateResponse("all_books.html", {"request": request})