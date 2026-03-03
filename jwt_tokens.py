
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from schemas import TokenData
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = os.getenv("ACCESS_TOKEN_EXPIRE_HOURS")


def create_access_token(data: TokenData):
    """Создаем JWT токен"""
    to_encode = {
        "sub": data.email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }

    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def verify_token(token: str, credentials_exception):
    """Проверяет JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if  payload.get("sub") is None:
            raise credentials_exception
        return True
    except JWTError:
        raise credentials_exception


def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])