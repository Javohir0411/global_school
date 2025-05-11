from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.schemas import StudentCreate, StudentInfo, StudentDetail, StudentGroupInfo, StudentUpdate
from app.db.session import get_db
from app.db.crud import (
    create_student,
    get_student,
    get_students,
    update_student,
    delete_student
)

student_router = APIRouter()

# from app.db.schemas import

@student_router.post("/students")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)


@student_router.get("/students", response_model=List[StudentGroupInfo])
def read_students(db: Session = Depends(get_db)):
    return get_students(db)


@student_router.get("/students/{student_id}", response_model=StudentDetail)
def read_student(student_id: int, db: Session = Depends(get_db)):
    return get_student(db, student_id)


@student_router.put("/students/{student_id}")
def modify_student(student_id: int, data_update: StudentUpdate, db: Session = Depends(get_db)):
    return update_student(db, student_id, data_update)


@student_router.delete("/students/{student_id}")
def remove_student(student_id: int, db: Session = Depends(get_db)):
    return delete_student(db, student_id)
