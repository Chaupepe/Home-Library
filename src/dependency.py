from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models import Users
from src.database import get_db
from src.security import verify_token
from src.templates import credentials_exception

def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=404, detail="Token is missing")
    token_data = verify_token(token, credentials_exception)
    user = db.query(Users).filter(Users.email == token_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
