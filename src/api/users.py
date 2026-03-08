from typing import Optional

from fastapi import APIRouter, Request, Response, HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from src.database import get_db
from src.templates import templates, credentials_exception
from src.security import decode_access_token, verify_token, hash_password, verify_password
from src.models import Users, Books

router = APIRouter()


@router.get("/root/profile")
async def profile(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=401, detail="Token is invalid")
    user = db.query(Users).filter(Users.email == decode_access_token(token).get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return  templates.TemplateResponse("profile.html", {"request": request, "user" : user})


@router.get("/root/profile/avatar")
async def get_avatar(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    payload = decode_access_token(token)
    user = db.query(Users).filter(Users.email == payload["sub"]).first()

    if not user:
        # Если аватар отсутствует, можно вернуть 404 или стандартное изображение
        raise HTTPException(status_code=404, detail="Avatar not found")
    return Response(content=user.avatar, media_type="image/jpeg")


@router.get("/root/profile/edit", response_class=HTMLResponse)
async  def edit_page( request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    payload = decode_access_token(token)
    user = db.query(Users).filter(Users.email == payload["sub"]).first()
    return templates.TemplateResponse("profile_edit.html", {"request": request, "user": user})


@router.post("/root/profile/edit")
async def edit_profile(
        request: Request,
        db: Session = Depends(get_db),
        name: str = Form(...),
        email: str = Form(...),
        password: Optional[str] = Form(None),
        new_password_1: Optional[str] = Form(None),
        new_password_2: Optional[str] = Form(None),
        avatar: UploadFile = File(None),
        delete:  Optional[bool] = Form(...)
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")

    payload = decode_access_token(token)
    user = db.query(Users).filter(Users.email == payload["sub"]).first()
    user.name = name
    user.email = email
    if password or new_password_1 or new_password_2:
        if not (password and new_password_1 and new_password_2):
            raise HTTPException(status_code=400, detail="All password fields are required to change password")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")
        if new_password_1 != new_password_2:
            raise HTTPException(status_code=400, detail="New password does not match")
        user.hashed_password = hash_password(new_password_1)
    if delete == True:
        user.remove(avatar)
    if avatar:
        avatar_bytes = await avatar.read()
        user.avatar = avatar_bytes
    db.commit()
    return templates.TemplateResponse("profile.html", {"request": request, "user" : user})


@router.get("/root/my_library", response_class=HTMLResponse)
async def my_library(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")

    user = db.query(Users).filter(Users.email == decode_access_token(token).get("sub")).first()
    books = user.books
    return templates.TemplateResponse("my_library.html", {"request": request, "books": books})


@router.post("/root/my_library")
async def my_library_del(
        request: Request,
        db: Session = Depends(get_db),
        book_id: int = Form(...)
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    user = db.query(Users).filter(Users.email == decode_access_token(token).get("sub")).first()
    print(book_id)
    book = db.query(Books).filter(Books.id == book_id).first()
    user.books.remove(book)
    books = user.books
    db.commit()
    return templates.TemplateResponse("my_library.html", {"request": request, "books": books})
