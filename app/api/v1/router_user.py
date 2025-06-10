from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.crud import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user
)
from app.db.schemas import UserCreate, UserOutput, UserDetail, UserUpdate

user_router = APIRouter()


# @user_router.post("/users", response_model=dict)
# def add_user(data: UserCreate, db: Session = Depends(get_db)):
#     return create_user(db, data)


@user_router.get("/users", response_model=List[UserOutput])
def read_users(db: Session = Depends(get_db)):
    return get_users(db)


@user_router.get("/users/{user_id}", response_model=UserDetail)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)


@user_router.put("/users/{user_id}")
def modify_user(user_id: int, data_update: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, data_update)


@user_router.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db, user_id)
