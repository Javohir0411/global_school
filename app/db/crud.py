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
    PaymentBase, PaymentUpdate, GroupUpdate, GroupCreate, TeacherUpdate, StudentUpdate, AttendanceUpdate
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
    # Guruhlar va studentlar alohida ko'rib chiqiladi
    teacher_data = data.model_dump(exclude={"teacher_groups", "teacher_students"})

    # Model obyektini yaratish
    teacher = Teachers(**teacher_data)

    # Guruhlar bilan bog'lash (agar berilgan bo'lsa)
    if data.teacher_groups:
        groups = db.query(Groups).filter(Groups.id.in_(data.teacher_groups)).all()
        teacher.teacher_groups.extend(groups)

    if data.teacher_students:
        students = db.query(Students).filter(Students.id.in_(data.teacher_students)).all()
        teacher.teacher_students.extend(students)

    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def get_teachers(db: Session):
    teachers = db.query(Teachers).options(
        joinedload(Teachers.teacher_groups),
        joinedload(Teachers.teacher_subject),
        joinedload(Teachers.teacher_students),
        joinedload(Teachers.attendance)
    ).all()

    if not teachers:
        raise HTTPException(status_code=404, detail="No teachers found")

    return teachers


def get_teacher(db: Session, teacher_id: int):
    return db.query(Teachers).options(
        joinedload(Teachers.teacher_groups),
        joinedload(Teachers.teacher_subject),
        joinedload(Teachers.teacher_students),
        joinedload(Teachers.attendance)
    ).filter(Teachers.id == teacher_id).first()


def update_teacher(db: Session, teacher_id: int, data_update: TeacherUpdate):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found !")

    updated_data = data_update.dict(exclude_unset=True)  # Faqat o'zgartirilgan maydonni oladi

    if "teacher_groups" in updated_data:
        group_ids = updated_data.pop("teacher_groups")
        teacher.teacher_groups = db.query(Groups).filter(Groups.id.in_(group_ids)).all()

    if "teacher_students" in updated_data:
        student_ids = updated_data.pop("teacher_students")
        teacher.teacher_students = db.query(Students).filter(Students.id.in_(student_ids)).all()

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
        joinedload(Students.student_teachers)
    ).all()


def get_student(db: Session, student_id: int):
    return db.query(Students).options(
        joinedload(Students.student_groups),
        joinedload(Students.student_attendance),
        joinedload(Students.student_payment),
        joinedload(Students.student_teachers)
    ).filter(Students.id == student_id).first()


def update_student(db: Session, student_id: int, data_update: StudentUpdate):
    student = db.query(Students).filter(Students.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found!")

    updated_data = data_update.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        if key == "student_groups":
            groups = db.query(Groups).filter(Groups.id.in_(value)).all()
            student.student_groups = groups
        elif key == "student_teachers":
            teachers = db.query(Teachers).filter(Teachers.id.in_(value)).all()
            student.student_teachers = teachers
        else:
            setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int):
    student = db.query(Students).filter(Students.id == student_id).first()
    db.delete(student)
    db.commit()
    return student


# ------------------- Group CRUD -----------------------

def create_group(db: Session, data: GroupCreate):
    group = Groups(**data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def get_groups(db: Session):
    return db.query(Groups).options(
        joinedload(Groups.group_subject),
        joinedload(Groups.attendance),
        joinedload(Groups.group_teachers),
        joinedload(Groups.group_students)
    ).all()


def get_group(db: Session, group_id: int):
    return db.query(Groups).options(
        joinedload(Groups.group_subject),
        joinedload(Groups.attendance),
        joinedload(Groups.group_teachers),
        joinedload(Groups.group_students)
    ).filter(Groups.id == group_id).first()


def update_group(db: Session, group_id: int, data_update: GroupUpdate):
    group = db.query(Groups).filter(Groups.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found !")

    update_data = data_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(group, key, value)

    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group_id: int):
    group = db.query(Groups).filter(Groups.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found !")

    db.delete(group)
    db.commit()
    return group


# ------------------- Payments CRUD -----------------------

def create_payment(db: Session, data: PaymentCreate):
    payment = Payments(**data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payments(db: Session):
    return db.query(Payments).options(
        joinedload(Payments.student)
    ).all()


def get_payment(db: Session, payment_id: int):
    return db.query(Payments).options(
        joinedload(Payments.student)
    ).filter(Payments.id == payment_id).first()


def update_payment(db: Session, payment_id: int, data_update: PaymentUpdate):
    payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found !")

    update_data = data_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)
    return payment


def delete_payment(db: Session, payment_id: int):
    payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found !")

    db.delete(payment)
    db.commit()
    return payment


# ------------------- Attendance CRUD -----------------------

def create_attendance(db: Session, data: AttendanceCreate):

    # Studentni va u student guruhga biriktirilganligini tekshirish!
    student = db.query(Students).filter(Students.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Bunday student mavjud emas")

    group = db.query(Groups).filter(Groups.id == data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Bunday guruh mavjud emas !")

    if group not in student.student_groups:
        raise HTTPException(
            status_code=404,
            detail="Student bu guruhga biriktirilmagan !"
        )

    #Teacher va guruhni tekshirish!
    teacher = db.query(Teachers).filter(Teachers.id == data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Bunday teacher mavjud emas!",
        )

    if group not in teacher.teacher_groups:
        raise HTTPException(
            status_code=404,
            detail="Teacher bu guruhga biriktirilmagan!"
        )

    subject = db.query(Subjects).filter(Subjects.id == data.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Bunday subject topilmadi!"
        )

    if group.group_subject_id != subject.id:
        raise HTTPException(
            status_code=404,
            detail="Subject bu guruhga biriktirilmagan"
        )

    if teacher.teacher_subject_id != subject.id:
        raise HTTPException(
            status_code=404,
            detail="Subject bu o'qituvchiga biriktirilmagan!"
        )

    attendance = Attendance(**data.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def get_attendances(db: Session):
    return db.query(Attendance).options(
        joinedload(Attendance.teacher),
        joinedload(Attendance.student),
        joinedload(Attendance.group),
        joinedload(Attendance.subject)
    ).all()


def get_attendance(db: Session, attendance_id: int):
    return db.query(Attendance).options(
        joinedload(Attendance.teacher),
        joinedload(Attendance.student),
        joinedload(Attendance.group),
        joinedload(Attendance.subject)
    ).filter(Attendance.id == attendance_id).first()


def update_attendance(db: Session, attendance_id: int, data_update: AttendanceUpdate):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found !")

    update_data = data_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(attendance, key, value)

    db.commit()
    db.refresh(attendance)
    return attendance


def delete_attendance(db: Session, attendance_id: int):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    db.delete(attendance)
    db.commit()
    return attendance


# ------------------- Subject CRUD -----------------------

def create_subject(db: Session, data: SubjectCreate):
    subject = Subjects(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def get_subjects(db: Session):
    return db.query(Subjects).all()


def get_subject_by_id(db: Session, subject_id: int):
    return db.query(Subjects).options(
        joinedload(Subjects.subject_group),
        joinedload(Subjects.subject_teacher),
        joinedload(Subjects.attendance)
    ).filter(Subjects.id == subject_id).first()


def update_subject(db: Session, subject_id: int, data_update: SubjectDetail):
    subject = db.query(Subjects).filter(Subjects.id == subject_id).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found !")

    update_data = data_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(subject, key, value)

    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject_id: int):
    subject = db.query(Subjects).filter(Subjects.id == subject_id).first()
    db.delete(subject)
    db.commit()
    return subject
