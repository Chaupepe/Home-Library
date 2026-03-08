from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.api.books import router as books_router


main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(users_router)
main_router.include_router(books_router)