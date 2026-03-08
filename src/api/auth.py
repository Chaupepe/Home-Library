from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse

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


@router.get("/root/sign_up", response_class=HTMLResponse)
async def signup(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("sign_up.html", context)


@router.post("/root/sign_up", response_class=HTMLResponse)
async def create_user(
        request: Request,
        user_data : UserCreate,
        db: Session = Depends(get_db),
):

    db_user = Users(name=user_data.name, email=user_data.email, hashed_password= hash_password(user_data.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return  templates.TemplateResponse("authorization.html", {"request": request})


@router.get("/root/authorization", response_class=HTMLResponse)
async def authorization(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("authorization.html", context)


@router.post("/root/authorization",)
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
    resp = templates.TemplateResponse(
        "profile.html",
        {"request": request, "user" : user}
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
