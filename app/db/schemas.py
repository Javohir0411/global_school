from __future__ import annotations
from pydantic import BaseModel, ConfigDict
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
    teacher_groups: Optional[List["GroupBase"]] = None
    teacher_students: Optional[List["StudentBase"]] = None


class TeacherGroupInfo(BaseModel):  # GroupDetail uchun
    id: int
    teacher_firstname: str
    teacher_lastname: str
    teacher_phone_number: str


class TeacherSubject(BaseModel):  # crud.py: get_subject funksiyasi uchun
    id: int
    teacher_firstname: str
    teacher_lastname: str


class TeacherOutput(BaseModel):  # crud.py get_teachers funksiyasi uchun
    id: int
    teacher_firstname: str
    teacher_lastname: str

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    teacher_firstname: str
    teacher_lastname: str
    teacher_phone_number: str
    teacher_subject_id: Optional[int] = None
    teacher_groups: Optional[List[int]] = []
    teacher_students: Optional[List[int]] = []


class TeacherUpdate(BaseModel):
    teacher_firstname: Optional[str] = None
    teacher_lastname: Optional[str] = None
    teacher_phone_number: Optional[str] = None
    teacher_subject_id: Optional[int] = None
    teacher_groups: Optional[List[int]] = []
    teacher_students: Optional[List[int]] = []


class TeacherDetail(TeacherBase):
    teacher_subject: Optional["SubjectBase"]  # ForwardRef ishlatish
    teacher_groups: Optional[List["GroupOutput"]] = []  # ForwardRef ishlatish
    teacher_students: Optional[List["StudentGroupInfo"]] = []  # ForwardRef ishlatish
    attendance: Optional[List["AttendanceBase"]] = []  # ForwardRef ishlatish


# Subject model
class SubjectBase(BaseModel, _Config):
    id: int
    subject_name: str


class SubjectCreate(BaseModel):
    subject_name: str


class SubjectResponse(SubjectBase):
    subject_teacher: List[TeacherSubject] = []
    subject_group: List[GroupSubject]


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


class StudentInfo(StudentBase):
    student_groups: list["GroupBase"]
    student_teachers: list[TeacherBase]

    class Config:
        model_config = ConfigDict(from_attributes=True)

class StudentPaymentInfo(BaseModel):
    id: int
    student_firstname: str
    student_lastname: str
    student_groups: List[GroupOutput]


    class Config:
        model_config = ConfigDict(from_attributes=True)

class StudentCreate(BaseModel, _Config):
    student_firstname: str
    student_lastname: str
    student_phone_number: str
    student_parents_fullname: str
    student_parents_phone_number: str
    student_additional_info: str
    student_teachers: Optional[List[int]] = []
    student_groups: Optional[List[int]] = []


class StudentUpdate(BaseModel):
    student_firstname: Optional[str] = None
    student_lastname: Optional[str] = None
    student_phone_number: Optional[str] = None
    student_parents_fullname: Optional[str] = None
    student_parents_phone_number: Optional[str] = None
    student_additional_info: Optional[str] = None
    student_teachers: Optional[List[int]] = []
    student_groups: Optional[List[int]] = []


class StudentDetail(StudentBase):
    student_groups: List["GroupOutput"] = []  # ForwardRef ishlatish
    student_attendance: List["AttendanceBase"] = []  # ForwardRef ishlatish
    student_payment: List["PaymentBase"] = []  # ForwardRef ishlatish
    student_teachers: List[TeacherOutput] = []


class StudentGroupInfo(BaseModel):  # GroupDetail uchun crud.py get_students uchun ham
    id: int
    student_firstname: str
    student_lastname: str


# Group model
class GroupBase(BaseModel, _Config):
    id: int
    group_name: str
    lesson_time: str
    lesson_days: List[str]
    group_subject_id: Optional[int] = None

    class Config:
        from_attributes = True


class GroupOutput(BaseModel):  # crud.py get_teacher funksiyasi uchun
    id: int
    group_name: str


class GroupCreate(BaseModel):
    group_name: str
    lesson_time: str
    lesson_days: List[str]
    group_subject_id: Optional[int] = None


class GroupUpdate(BaseModel):
    group_name: Optional[str] = None
    lesson_time: Optional[str] = None
    lesson_days: Optional[List[str]] = []
    group_subject_id: Optional[int] = None


class GroupDetail(GroupBase):
    group_subject: Optional[SubjectBase] = None
    group_teachers: List[TeacherGroupInfo]
    group_students: List[StudentGroupInfo]
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class GroupSubject(BaseModel):  # crud.py: get_subjects funksiyasi uchun
    id: int
    group_name: str
    lesson_time: str


# Payments model
class PaymentBase(BaseModel, _Config):
    id: int
    payment_date: date
    payment_amount: float


class PaymentCreate(BaseModel):
    student_id: int
    payment_date: date
    payment_amount: float

class PaymentsOutput(BaseModel):
    id: int
    student: StudentGroupInfo
    payment_date: date
    payment_amount: float


class PaymentUpdate(PaymentBase):
    payment_date: Optional[date]
    payment_amount: Optional[float]


class PaymentDetail(PaymentBase):
    id: int
    student: StudentPaymentInfo
    payment_date: date
    payment_amount: float
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


class AttendanceUpdate(BaseModel):
    teacher_id: Optional[int] = None
    student_id: Optional[int] = None
    group_id: Optional[int] = None
    subject_id: Optional[int] = None
    attendance_date: Optional[date] = None
    status: AttendanceEnum = AttendanceEnum.ABSENT


class AttendancesOutput(BaseModel):
    id: int
    attendance_date: date
    group: GroupOutput

class AttendanceDetail(BaseModel):
    id: int
    attendance_date: date
    status: AttendanceEnum
    teacher: TeacherOutput
    student: StudentGroupInfo
    group: GroupOutput
    subject: SubjectCreate
    created_at: datetime
    updated_at: datetime


TeacherDetail.update_forward_refs()
SubjectDetail.update_forward_refs()
StudentDetail.update_forward_refs()
GroupDetail.update_forward_refs()
PaymentDetail.update_forward_refs()
AttendanceDetail.update_forward_refs()
