from app.core.security import create_access_token, verify_password, create_refresh_token
from app.db.schemas import UserCreate, UserLogin, AdminDetail, TeacherDetail, TeacherGroupInfo
from app.db.models import User, Admins, Teachers, Groups
from app.db.crud import create_user, save_refresh_token
from app.core.utils import get_user_by_username
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, Request
from app.core.config import settings
from fastapi.params import Depends
from app.db.session import get_db
from datetime import timedelta
from jose import JWTError
import logging
import jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register(user: UserCreate, db: Session):
    db_user_username = get_user_by_username(user.username, db)
    if db_user_username:
        raise HTTPException(status_code=409, detail="Bunday username bilan avval ro'yxatdan o'tilgan !")

    return create_user(db, user)


def login(data: UserLogin, db: Session):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Noto'g'ri username yoki password kiritildi !")

    logger.info(f"User username: {data.username}")
    logger.info(f"User password: {data.password}")
    logger.info(f"Verify result: {data.password, user.password}")

    if user.role.value == "admin":
        admin = db.query(Admins).filter(Admins.id == user.admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found !")

        admin_access_token = create_access_token(
            data={"sub": user.username,
                  "user_id": user.id,
                  "role": user.role,
                  "is_registered": True,
                  "details": AdminDetail.from_orm(admin).dict()
                  },
            expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info(f"Yaratilgan admin access token: {admin_access_token}")

        admin_refresh_token = create_refresh_token(
            data={"sub": user.username},
            expire_delta=timedelta(days=30)
        )

        return {
            "access_token": admin_access_token,
            "refresh_token": admin_refresh_token,
            "token_type": "bearer",
        }


    elif user.role.value == "teacher":
        if not user.teacher_id:
            raise HTTPException(status_code=400, detail="Userga biriktirilgan teacher_id mavjud emas")
        teacher = db.query(Teachers).options(
            joinedload(Teachers.teacher_groups).joinedload(Groups.group_subject),
            joinedload(Teachers.teacher_groups).joinedload(Groups.group_students)
        ).filter(Teachers.id == user.teacher_id).first()

        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found !")

        teacher_access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role.value,
                "is_registered": True,
            },
            expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        teacher_refresh_token = create_refresh_token(
            data={"sub": user.username},
            expire_delta=timedelta(days=30)
        )

        return {
            "access_token": teacher_access_token,
            "refresh_token": teacher_refresh_token,
            "token_type": "bearer",
        }


def logout():
    return {"message": "Foydalanuvchi muvaffaqiyatli tizimdan chiqarildi. (Fronent tokenni o'chirib qo'yadi)"}

    # access_token = create_access_token(
    #     data={"sub": user.username,
    #           "user_id": user.id,
    #           "is_registered": True},
    #     expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # )
    # logger.info(f"Yaratilgan access token: {access_token}")
    #
    # refresh_token = create_refresh_token(
    #     data={"sub": user.username},
    #     expire_delta=timedelta(days=30)
    # )
    #
    # base_response = {
    #     "id": user.id,
    #     "username": user.username,
    #     "role": user.role,
    #     "access_token": access_token,
    #     "refresh_token": refresh_token,
    #     "token_type": "bearer",
    # }
