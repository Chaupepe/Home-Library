
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from src.schemas import TokenData

from src.templates import pwd_context
from src.database import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


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
        email = payload.get("sub")
        if  email is None:
            raise credentials_exception
        return TokenData(email=email)
    except JWTError:
        raise credentials_exception


def hash_password(password: str) -> str:
    """Хэширует пароль"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)

