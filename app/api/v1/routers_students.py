from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.schemas import StudentCreate
from app.db.session import get_db
from app.db.crud import (
    create_student,
    get_student,
    get_students,
    update_student,
    delete_student
)

student_routers = APIRouter()

# from app.db.schemas import

@student_routers.post("/students")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)


@student_routers.get("/students")
def read_students(db: Session = Depends(get_db)):
    return get_students(db)


@student_routers.get("/students/{student_id}")
def read_student(student_id: int, db: Session = Depends(get_db)):
    return get_student(db, student_id)


@student_routers.put("/students/{student_id}")
def modify_student(student_id: int, data_update: StudentCreate, db: Session = Depends(get_db)):
    return update_student(db, student_id, data_update)


@student_routers.delete("/students/{student_id}")
def remove_student(student_id: int, db: Session = Depends(get_db)):
    return delete_student(db, student_id)
