from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from sqlalchemy.orm import Session

from src.database import get_db
from src.templates import templates
from src.security import hash_password, create_access_token, verify_password
from src.schemas import TokenData, UserCreate, UserLogin
from src.models import Users

router = APIRouter()



@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("root.html", context)


@router.get("/auth/register", response_class=HTMLResponse)
async def signup(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("sign_up.html", context)


@router.post("/auth/register", response_class=HTMLResponse)
async def create_user(
        request: Request,
        user_data : UserCreate,
        db: Session = Depends(get_db),
):
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = Users(
        name=user_data.name,
        email=user_data.email,
        hashed_password= hash_password(user_data.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return  templates.TemplateResponse("authorization.html", {"request": request})


@router.get("/auth/login", response_class=HTMLResponse)
async def authorization(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("authorization.html", context)


@router.post("/auth/login",)
async def log_in(
        request: Request,
        user_data : UserLogin,
        db: Session = Depends(get_db),

):

    user = db.query(Users).filter(Users.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if  not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password mismatch")
    token = create_access_token(TokenData(email=user.email))
    resp = JSONResponse(content={"ok": True})
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


@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("token")
    return response