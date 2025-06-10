from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
import logging
import jwt
from sqlalchemy.orm import Session

from app.core.register import register, login, logout
from app.core.security import create_access_token
from app.db.models import User
from app.db.schemas import UserCreate, UserOutput, Token, UserLogin
from app.db.session import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

authentication_router = APIRouter()

@authentication_router.post("/register", response_model=UserOutput)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return register(user, db)

@authentication_router.post("/login", response_model=Token)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    return login(data, db)

@authentication_router.post("/logout")
def logout_user():
    return logout()


@authentication_router.post("/reset-password")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token({"sub": user.user_email}, expire_delta=timedelta(hours=1))

    # (YUBORISH qismi – hozircha faqat logga chiqaramiz)
    logger.info(f"Parolni tiklash havolasi: http://localhost:8000/reset-password?token={reset_token}")

    return {"msg": "Parolni tiklash havolasi emailingizga yuborildi"}
