from typing import Optional

from fastapi import APIRouter, Request, Response, HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from src.schemas import AddBookToUser
from src.database import get_db
from src.templates import templates
from src.security import hash_password, verify_password
from src.models import Users, Books
from src.dependency import get_current_user

router = APIRouter()


@router.get("/profile")
async def profile(
        request: Request,
        current_user: Users = Depends(get_current_user)
):
    return  templates.TemplateResponse("profile.html", {"request": request, "user" : current_user})


@router.get("/profile/avatar")
async def get_avatar(
    current_user: Users = Depends(get_current_user)
):
    return Response(content=current_user.avatar, media_type="image/jpeg")


@router.get("/profile/edit", response_class=HTMLResponse)
async  def edit_page(
        request: Request,
        current_user: Users = Depends(get_current_user)
):
    return templates.TemplateResponse("profile_edit.html", {"request": request, "user": current_user})


@router.post("/profile/edit")
async def edit_profile(
        request: Request,
        db: Session = Depends(get_db),
        name: str = Form(...),
        email: str = Form(...),
        password: Optional[str] = Form(None),
        new_password_1: Optional[str] = Form(None),
        new_password_2: Optional[str] = Form(None),
        avatar: UploadFile = File(None),
        delete:  Optional[bool] = Form(None),
        current_user: Users = Depends(get_current_user)
):
    current_user.name = name
    current_user.email = email
    if password or new_password_1 or new_password_2:
        if not (password and new_password_1 and new_password_2):
            raise HTTPException(status_code=400, detail="All password fields are required to change password")
        if not verify_password(password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")
        if new_password_1 != new_password_2:
            raise HTTPException(status_code=400, detail="New password does not match")
        current_user.hashed_password = hash_password(new_password_1)
    if delete:
        current_user.avatar = None
    elif avatar:
        avatar_bytes = await avatar.read()
        current_user.avatar = avatar_bytes
    db.commit()
    return templates.TemplateResponse("profile.html", {"request": request, "user" : current_user})


@router.get("/profile/books", response_class=HTMLResponse)
async def my_library(
        request: Request,
        current_user: Users = Depends(get_current_user)
):
    books = current_user.books
    return templates.TemplateResponse("my_library.html", {"request": request, "books": books})


@router.post("/profile/books")
async def my_library_del(
        request: Request,
        add_book_data: AddBookToUser,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    book = db.query(Books).filter(Books.id == add_book_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book not in current_user.books:
        raise HTTPException(status_code=400, detail="Book not in your library")
    current_user.books.remove(book)
    books = current_user.books
    db.commit()
    return templates.TemplateResponse("my_library.html", {"request": request, "books": books})
