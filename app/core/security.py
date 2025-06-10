from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Security
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings
from app.db.models import User
from jose import jwt, JWTError
from dotenv import load_dotenv
import logging
import os
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict, expire_delta: timedelta):
#     to_encode = data.copy()
#     expire = datetime.now() + expire_delta
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

def create_access_token(data: dict, expire_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expire_delta
    to_encode.update({"exp": expire})

    to_encode.update({"user_id": data.get("user_id"), "is_registered": True})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session):
    print(f"Token turi: {type(token)}")  # Tokenning turini chiqaramiz
    print(f"Token: {token}")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id: int = payload.get("user_id")
        is_registered: bool = payload.get("is_registered")
        logging.info("User_id: %s", user_id)

        if not user_id or not is_registered:
            logging.info("User_id: %s", user_id)
            raise HTTPException(status_code=403, detail="Foydalanuvchi ro'yxatdan o'tmagan yoki token no'to'gri ekan")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print("Foydalanuvchi topilmadi !")
            raise HTTPException(status_code=404, detail="Bunday foydalanuvchi topilmadi !")
        print(f"Topilgan foydalanuvchi !: {user}")
        return user

    except JWTError as e:
        print(f"Token verifikatsiyada xatolik: {e}")
        raise HTTPException(status_code=401, detail="Noto'g'ri token")


def create_refresh_token(data: dict, expire_delta: timedelta = timedelta(30)):
    to_encode = data.copy()
    expire = datetime.now() + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt