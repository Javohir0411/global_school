from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# PostgreSQL bazasi bilan bog‘lanish uchun SQLAlchemy engine yaratamiz
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)

# SessionLocal - Har bir so‘rov uchun yangi sessiya yaratish
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


def get_db():  # Har bir so‘rov uchun alohida sessiya yaratish va yopish
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # So‘rov tugagach sessiya yopiladi