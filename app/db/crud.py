from fastapi import HTTPException

from app.db.models import (
    Teachers,
    Students,
    Subjects,
    Groups,
    Payments,
    Attendance
)
from app.db.schemas import (
    TeacherBase,
    TeacherCreate,
    TeacherDetail,

    SubjectBase,
    SubjectDetail,
    SubjectCreate,

    StudentBase,
    StudentDetail,
    StudentCreate,

    GroupBase,
    GroupDetail,

    AttendanceBase,
    AttendanceDetail,
    AttendanceCreate,

    PaymentDetail,
    PaymentCreate,
    PaymentBase
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from typing import List
import logging
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------- Teacher CRUD -----------------------

def create_teachers(db: Session, data: TeacherCreate):
    teacher = Teachers(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def get_teachers(db: Session):
    return db.query(Teachers).options(
        joinedload(Teachers.teacher_groups),
        joinedload(Teachers.teacher_subject),
        joinedload(Teachers.teacher_students),
        joinedload(Teachers.attendance)
    ).all()


def get_teacher(db: Session, teacher_id: int):
    return db.query(Teachers).options(
        joinedload(Teachers.teacher_groups),
        joinedload(Teachers.teacher_subject),
        joinedload(Teachers.teacher_students),
        joinedload(Teachers.attendance)
    ).filter(Teachers.id == teacher_id).first()


def update_teacher(db: Session, teacher_id: int, data_update: TeacherCreate):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found !")

    updated_data = data_update.dict(exclude_unset=True)  # Faqat o'zgartirilgan maydonni oladi

    for key, value in updated_data.items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)
    return teacher


def delete_teacher(db: Session, teacher_id: int):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found !")

    db.delete(teacher)
    db.commit()
    return teacher

# ------------------- Student CRUD -----------------------

def create_student(db: Session, data: StudentCreate):
    student_data = data.model_dump(exclude={"student_groups", "student_teachers"})
    student = Students(**student_data)

    if data.student_teachers:
        teachers = db.query(Teachers).filter(Teachers.id.in_(data.student_teachers)).all()
        student.student_teachers.extend(teachers)

    if data.student_groups:
        groups = db.query(Groups).filter(Groups.id.in_(data.student_groups)).all()
        student.student_groups.extend(groups)

    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def get_students(db: Session):
    return db.query(Students).options(
        joinedload(Students.student_groups),
        joinedload(Students.student_attendance),
        joinedload(Students.student_payment),
        joinedload(Students.student_teachers)
    ).all()

def get_student(db: Session, student_id: int):
    return db.query(Students).options(
        joinedload(Students.student_groups),
        joinedload(Students.student_attendance),
        joinedload(Students.student_payment),
        joinedload(Students.student_teachers)
    ).filter(Students.id == student_id).first()

def update_student(db: Session, student_id: int, data_update: StudentCreate):
    student = db.query(Students).filter(Students.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found !")

    updated_data = data_update.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found !")

    db.delete(student)
    db.commit()
    return student