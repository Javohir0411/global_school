from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.crud import (
    create_admin,
    get_admins,
    get_admin,
    update_admin,
    delete_admin
)
from app.db.schemas import AdminCreate, AdminOutput, AdminDetail, AdminUpdate

admin_router = APIRouter()


@admin_router.post("/admins")
def add_admin(data: AdminCreate, db: Session = Depends(get_db)):
    return create_admin(db, data)


@admin_router.get("/admins", response_model=List[AdminOutput])
def read_admins(db: Session = Depends(get_db)):
    return get_admins(db)


@admin_router.get("/admins/{admin_id}", response_model=AdminDetail)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    return get_admin(db, admin_id)


@admin_router.put("/admins/{admin_id}")
def modify_admin(admin_id: int, data_update: AdminUpdate, db: Session = Depends(get_db)):
    return update_admin(db, admin_id, data_update)


@admin_router.delete("/admins/{admin_id}")
def remove_admin(admin_id: int, db: Session = Depends(get_db)):
    return delete_admin(db, admin_id)
