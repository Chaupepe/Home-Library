from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.engine import URL

load_dotenv(encoding='utf-8')

DB_USER = os.getenv("DB_USER").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD").strip()
DB_HOST = os.getenv("DB_HOST").strip()
DB_PORT = os.getenv("DB_PORT").strip()
DB_NAME = os.getenv("DB_NAME").strip()



url_object = URL.create(
    drivername="postgresql",
    username=DB_USER,
    password=DB_PASSWORD,  # будет автоматически закодирован
    host=DB_HOST,
    database=DB_NAME,
    port=DB_PORT
)

engine = create_engine(url_object,connect_args={'client_encoding': 'utf8'})  # передаём объект URL, а не строку
engine.dispose()


SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

