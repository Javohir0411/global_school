from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.crud import (
    create_teachers,
    get_teachers,
    get_teacher,
    update_teacher,
    delete_teacher
)
from app.db.schemas import TeacherBase, TeacherDetail, TeacherCreate, TeacherUpdate, TeacherOutput

teacher_router = APIRouter()
# Teacher modeli uchun router

@teacher_router.post("/teachers")
def add_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    return create_teachers(db, teacher)

@teacher_router.get("/teachers", response_model=List[TeacherOutput])
def read_teachers(db: Session = Depends(get_db)):
    return get_teachers(db)

@teacher_router.get("/teachers/{teacher_id}", response_model = TeacherDetail)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return get_teacher(db, teacher_id)

@teacher_router.put("/teachers/{teacher_id}")
def modify_teacher(teacher_id: int, data_update: TeacherUpdate, db: Session = Depends(get_db)):
    return update_teacher(db, teacher_id, data_update)

@teacher_router.delete("/teachers/{teacher_id}")
def remove_teacher(teacher_id: int, db: Session = Depends(get_db)):
    return delete_teacher(db, teacher_id)