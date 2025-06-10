from fastapi import HTTPException
from app.core.security import hash_password

from app.db.models import (
    Teachers,
    Students,
    Subjects,
    Groups,
    Payments,
    Attendance,
    Admins,
    User
)
from app.db.schemas import (
    TeacherBase,
    TeacherCreate,
    TeacherDetail,
    TeacherUpdate,

    SubjectBase,
    SubjectDetail,
    SubjectCreate,

    StudentBase,
    StudentDetail,
    StudentCreate,
    StudentUpdate,

    GroupBase,
    GroupDetail,

    AttendanceBase,
    AttendanceDetail,
    AttendanceCreate,
    AttendanceUpdate,

    PaymentDetail,
    PaymentCreate,
    PaymentBase,
    PaymentUpdate,

    GroupUpdate,
    GroupCreate,
    TeacherUnassignRequest,

    AdminCreate,
    AdminOutput,
    AdminDetail,
    AdminUpdate,

    UserCreate,
    UserUpdate
)
from datetime import datetime, timedelta, date
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


def delete_group_from_teacher(teacher_id: int, group_id: int, db: Session):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher topilmadi !")

    group = db.query(Groups).filter(Groups.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group topilmadi !")

    if group not in teacher.teacher_groups:
        raise HTTPException(status_code=400, detail="Group Teacher-ga bog'lanmagan !")

    teacher.teacher_groups.remove(group)
    db.commit()
    return {"detail": f"Group {group_id} Teacher {teacher_id} da muvaffaqiyatli uzildi !"}


def delete_student_from_teacher(teacher_id: int, student_id: int, db: Session):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher topilmadi !")

    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi !")

    if student not in teacher.teacher_students:
        raise HTTPException(status_code=400, detail="Student Teacher-ga bog'lanmagan !")

    teacher.teacher_students.remove(student)
    db.commit()
    return {"detail": f"Student {student_id} Teacher {teacher_id} da muvaffaqiyatli uzildi !"}


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
            # Avvalgi o'qituvchilarni o'chirish (munosabatni tozalash)
            student.student_teachers.clear()
            # Keyin yangi o'qituvchilarni qo'shish
            student.student_teachers.extend(teachers)
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


def delete_teacher_from_student(student_id: int, teacher_id: int, db: Session):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found !")

    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found !")

    if teacher not in student.student_teachers:
        raise HTTPException(status_code=404, detail="This teacher is not assigned to the student !")

    student.student_teachers.remove(teacher)
    db.commit()
    return {"detail": f"Teacher {teacher_id} has been unassigned from student {student_id}"}


def delete_group_from_student(student_id: int, group_id: int, db=Session):
    student = db.query(Students).filter(Students.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found !")

    group = db.query(Groups).filter(Groups.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found !")

    if group not in student.student_groups:
        raise HTTPException(status_code=400, detail="Group not linked to this student")

    student.student_groups.remove(group)
    db.commit()
    return {"detail": f"Group {group_id} has been unassigned from student {student_id}"}


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
    today = date.today()

    teacher = db.query(Teachers).filter(Teachers.id == data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found !")

    group = db.query(Groups).filter(Groups.id == data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found !")

    if group not in teacher.teacher_groups:
        raise HTTPException(status_code=404, detail="Group has not been assigned to this teacher !")

    subject = db.query(Subjects).filter(Subjects.id == group.group_subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found !")

    if teacher.teacher_subject_id != subject.id:
        raise HTTPException(status_code=404, detail="Subject has not been assigned to this teacher !")

    result = []
    for item in data.attendance:
        student = db.query(Students).filter(Students.id == item.student_id).first()
        if not student:
            continue

        if group not in student.student_groups:
            raise HTTPException(status_code=404, detail="Student has not been assigned to this group")

        existing = db.query(Attendance).filter_by(
            student_id=item.student_id,
            group_id=data.group_id,
            attendance_date=today
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Attendance has been confirmed for this date!")

        attendance = Attendance(
            teacher_id=data.teacher_id,
            student_id=item.student_id,
            group_id=data.group_id,
            subject_id=subject.id,
            attendance_date=today,
            status=item.status.value
        )
        db.add(attendance)
        result.append({
            "student": f"{student.student_firstname} {student.student_lastname}",
            "status": f"{item.status.value}"
        })
    db.commit()
    return {
        "teacher": f"{teacher.teacher_firstname} {teacher.teacher_lastname}",
        "group": group.group_name,
        "group_subject": subject.subject_name,
        "lesson_date": today.strftime("%d-%m-%Y"),
        "lesson_days": "-".join(group.lesson_days),
        "lesson_time": group.lesson_time,
        "attendance": result
    }


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


# ------------------- Admin CRUD -----------------------

def create_admin(db: Session, data: AdminCreate):
    admin = Admins(**data.model_dump())
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def get_admins(db: Session):
    return db.query(Admins).options(
        joinedload(Admins.admin_account),
    ).all()


def get_admin(db: Session, admin_id: int):
    admin = db.query(Admins).options(
        joinedload(Admins.admin_account)
    ).filter(Admins.id == admin_id).first()

    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin id = {admin_id} not found !")

    return admin

def update_admin(db: Session, admin_id: int, data_update: AdminUpdate):
    admin = db.query(Admins).filter(Admins.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found !")

    updated_data = data_update.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin


def delete_admin(db: Session, admin_id: int):
    admin = db.query(Admins).filter(Admins.id == admin_id).first()
    db.delete(admin)
    db.commit()
    return admin


# ------------------- User CRUD -----------------------

def create_user(db: Session, data: UserCreate):
    # 1. Password-ni hash qilamiz
    hashed_password = hash_password(data.password)

    # 2. Data modeldan password-ni chiqarib tashlaymiz, chunki uni alohida qo'shmoqchimiz
    user_data = data.model_dump(exclude={"password"})

    # 3. User modeliga hashed_password ni qo'shamiz
    user = User(**user_data, password=hashed_password)

    # 4. Bazaga yozamiz
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "role": user.role,
        "username": user.username,
        "teacher_id": user.teacher_id,
        "admin_id": user.admin_id
    }

def get_users(db: Session):
    return db.query(User).options(
        joinedload(User.teacher),
        joinedload(User.admin)
    ).all()


def get_user(db: Session, user_id: int):
    user = db.query(User).options(
        joinedload(User.teacher),
        joinedload(User.admin)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found !")

    return user

def update_user(db: Session, user_id: int, data_update: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found !")

    updated_data = data_update.dict(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found !")

    db.delete(user)
    db.commit()
    return user


# ------------------- Save Refresh Token -----------------------

def save_refresh_token(db, user_id: int, refresh_token: str):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.info(f"User id = {user_id} topilmadi !")
        raise HTTPException(status_code=404, detail=f"{user_id} id raqamiga ega foydalanuvchi topilmadi !")

    logger.info(f"{user_id} id raqamiga ega foydalanuvchi topildi, token yaratilmoqda...")
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)
    logger.info(f"Refresh token bazaga saqlandi, refresh token: {user.refresh_token}")
    return user


"""
***chornavik***

username va password

user = username boyicha qidiruv va username == username ->
-> user_id = user.id

user = User.id == user_id
if user:
    user.refresh_token = refresh_token
"""