from fastapi import HTTPException, status
from fastapi.templating import Jinja2Templates

from passlib.context import CryptContext


templates = Jinja2Templates(directory="templates")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")