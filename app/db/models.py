from sqlalchemy import (Column,
                        Integer,
                        String,
                        ForeignKey,
                        Text,
                        Float,
                        Boolean,
                        Table,
                        Date)
from sqlalchemy.orm import relationship
from app.db.base import Base

teacher_group_association = Table(
    "teacher_group_association",
    Base.metadata,
    Column("teachers_id", ForeignKey("teachers.id"), primary_key=True),
    Column("groups_id", ForeignKey("groups.id"), primary_key=True)
)

student_group_association = Table(
    "student_group_association",
    Base.metadata,
    Column("students_id", ForeignKey("students.id"), primary_key=True),
    Column("groups_id", ForeignKey("groups.id"), primary_key=True)
)

teacher_students_association = Table(
    "teacher_students_association",
    Base.metadata,
    Column("teachers_id", ForeignKey("teachers.id"), primary_key=True),
    Column("students_id", ForeignKey("students.id"), primary_key=True)
)


class Teachers(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    teacher_firstname = Column(String)
    teacher_lastname = Column(String)
    teacher_phone_number = Column(String)
    teacher_subject = Column(String)

    teacher_groups = relationship("Groups",
                                  secondary=teacher_group_association,
                                  back_populates="group_teachers")  # Ustoz uchun biriktirilgan guruhlar

    teacher_students = relationship("Students",
                                    secondary=teacher_students_association,
                                    back_populates="teachers")  # Ustoz uchun biriktirilgan studentlar


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    student_firstname = Column(String)
    student_lastname = Column(String)
    student_phone_number = Column(String)

    student_groups = relationship("Groups", secondary=student_group_association, back_populates="group_students")

    student_additional_info = Column(Text)
    student_attendance = relationship("Attendance", back_populates="student", passive_deletes=True)
    student_payment = relationship("Payments", back_populates="student")
    student_parents_fullname = Column(String)
    student_parents_phone_number = Column(String)

    teachers = relationship("Teachers", secondary=teacher_students_association, back_populates="students")


class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    group_name = Column(String)
    lesson_time = Column(String)
    lesson_days = Column(String)
    group_subject = Column(String)
    attendance = relationship("Attendance", back_populates="group", passive_deletes=True)

    # Guruh ustozi
    group_teachers = relationship("Teachers", secondary=teacher_group_association, back_populates="teacher_groups")

    # Guruh talabalari
    group_students = relationship("Students", secondary=student_group_association, back_populates="student_groups")


class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    student = relationship("Students", back_populates="student_payment", passive_deletes=True)
    payment_date = Column(Date)
    payment_amount = Column(Float)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    student = relationship("Students", back_populates="student_attendance", passive_deletes=True)

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    group = relationship("Groups", back_populates="attendance", passive_deletes=True)

    attendance_date = Column(Date)
    is_present = Column(Boolean)
