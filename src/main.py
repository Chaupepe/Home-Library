from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.database import engine
from src.models import Base
from src.api import main_router


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(main_router)





if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
