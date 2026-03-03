from fastapi import FastAPI, Request, Form , Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_db, engine
from models_users import Users, Books, Base
from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jwt_tokens import create_access_token, verify_token, decode_access_token
from schemas import TokenData
from datetime import date


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def hash_password(password: str) -> str:
    """Хэширует пароль"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("root.html", context)


@app.get("/root/my_library", response_class=HTMLResponse)
async def my_library(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")

    books = db.query(Books).filter(Books.users.any()).all()
    return templates.TemplateResponse("my_library.html", {"request": request, "books": books})


@app.get("/root/sign_up", response_class=HTMLResponse)
async def signup(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("sign_up.html", context)


@app.post("/root/sign_up", response_class=HTMLResponse)
async def create_user(
        request: Request,
        db: Session = Depends(get_db),
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):

    db_user = Users(name=name, email=email, hashed_password= hash_password(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return  templates.TemplateResponse("authorization.html", {"request": request})


@app.get("/root/authorization", response_class=HTMLResponse)
async def authorization(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("authorization.html", context)


@app.post("/root/authorization",)
async def log_in(
        request: Request,
        db: Session = Depends(get_db),
        email: str = Form(...),
        password: str = Form(...)
):

    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if  not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password mismatch")
    token = create_access_token(TokenData(email=user.email))
    resp = templates.TemplateResponse(
        "profile.html",
        {"request": request, "name": user.name, "email": user.email}
    )
    resp.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
        path="/",
    )
    return  resp


@app.get("/root/profile")
async def profile(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    user = db.query(Users).filter(Users.email == token.decode("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return  templates.TemplateResponse("profile.html", {"request": request,"name" : user.name, "email" : user.email})


@app.post("/root/profile/add_book")
def add_book(
        request: Request,
        db: Session = Depends(get_db),
        name: str = Form(...),
        author: str = Form(...),
        publisher: str = Form(...),
        year_of_publication: date = Form(...),
        state_author: str = Form(...),
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    book = Books(
        name = name,
        author = author,
        year_of_publication = year_of_publication,
        state_author = state_author,
        publisher = publisher
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return templates.TemplateResponse("add_book.html", {"request" : request})


@app.get("/root/profile/add_book")
async def add_book(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    context = {
        "request": request
    }
    return templates.TemplateResponse("add_book.html", context)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)


@app.get("/root/profile/all_books", response_class=HTMLResponse)
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


@app.post("/root/profile/all_books")
async def add_book_to_user(
        request: Request,
        db: Session = Depends(get_db),
        book_id: int = Form(...),
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    if not verify_token(token, credentials_exception):
        raise HTTPException(status_code=404, detail="Token is invalid")
    payload = decode_access_token(token)
    user = db.query(Users).filter(Users.email == payload["sub"]).first()
    book = db.query(Books).filter(Books.id == book_id).first()
    user.books.append(book)
    db.commit()
    return templates.TemplateResponse("all_books.html", {"request": request})

