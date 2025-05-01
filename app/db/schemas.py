from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from app.enums import AttendanceEnum

# Modellar va ForwardRef (agar kerak bo'lsa)
class _Config:
    model_config = dict(from_attributes=True)

# Teacher model
class TeacherBase(BaseModel, _Config):
    id: int
    teacher_firstname: str
    teacher_lastname: str
    teacher_phone_number: str
    teacher_subject_id: Optional[int]
    teacher_groups: Optional[List[int]] = None
    teacher_students: Optional[List[int]] = None

class TeacherCreate(BaseModel):
    teacher_firstname: str
    teacher_lastname: str
    teacher_phone_number: str
    teacher_subject_id: Optional[int] = None
    teacher_groups: Optional[List[int]] = []
    teacher_students: Optional[List[int]] = []

class TeacherDetail(TeacherBase):
    teacher_subject: Optional["SubjectBase"]  # ForwardRef ishlatish
    teacher_groups: Optional[List["GroupBase"]] = []  # ForwardRef ishlatish
    teacher_students: Optional[List["StudentBase"]] = []  # ForwardRef ishlatish
    attendance: Optional[List["AttendanceBase"]] = []  # ForwardRef ishlatish


# Subject model
class SubjectBase(BaseModel, _Config):
    id: int
    subject_name: str

class SubjectCreate(BaseModel):
    subject_name: str

class SubjectDetail(SubjectBase):
    subject_teacher: List[TeacherBase] = []
    subject_groups: List["GroupBase"] = []  # ForwardRef ishlatish
    created_at: datetime
    updated_at: datetime


# Student model
class StudentBase(BaseModel, _Config):
    id: int
    student_firstname: str
    student_lastname: str
    student_phone_number: str
    student_parents_fullname: str
    student_parents_phone_number: str
    student_additional_info: str
    created_at: datetime
    updated_at: datetime

class StudentCreate(BaseModel, _Config):
    student_firstname: str
    student_lastname: str
    student_phone_number: str
    student_parents_fullname: str
    student_parents_phone_number: str
    student_additional_info: str
    student_teachers: Optional[List[int]] = []
    student_groups: Optional[List[int]] = []
    created_at: datetime
    updated_at: datetime

class StudentDetail(StudentBase):
    student_groups: List["GroupBase"] = []  # ForwardRef ishlatish
    student_attendance: List["AttendanceBase"] = []  # ForwardRef ishlatish
    student_payment: List["PaymentBase"] = []  # ForwardRef ishlatish
    student_teachers: List[TeacherBase] = []


# Group model
class GroupBase(BaseModel, _Config):
    id: int
    group_name: str
    lesson_time: str
    lesson_days: List[str]
    group_subject_id: Optional[int] = None

class GroupDetail(GroupBase):
    group_subject: SubjectBase
    group_teachers: List[TeacherBase] = []
    group_students: List[StudentBase] = []
    created_at: datetime
    updated_at: datetime


# Payments model
class PaymentBase(BaseModel, _Config):
    id: int
    payment_date: date
    payment_amount: float

class PaymentCreate(BaseModel):
    student_id: int
    payment_date: date
    payment_amount: float

class PaymentDetail(PaymentBase):
    student: StudentBase
    created_at: datetime
    updated_at: datetime


# Attendance model
class AttendanceBase(BaseModel, _Config):
    id: int
    attendance_date: date
    status: AttendanceEnum

class AttendanceCreate(BaseModel):
    teacher_id: int
    student_id: int
    group_id: int
    subject_id: int
    attendance_date: date
    status: AttendanceEnum = AttendanceEnum.ABSENT

class AttendanceDetail(AttendanceBase):
    teacher: TeacherBase
    student: StudentBase
    group: GroupBase
    subject: SubjectBase
    created_at: datetime
    updated_at: datetime


TeacherDetail.update_forward_refs()
SubjectDetail.update_forward_refs()
StudentDetail.update_forward_refs()
GroupDetail.update_forward_refs()
PaymentDetail.update_forward_refs()
AttendanceDetail.update_forward_refs()