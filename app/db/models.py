from sqlalchemy import (Column,
                        Integer,
                        String,
                        ForeignKey,
                        Text,
                        Float,
                        Boolean,
                        Table,
                        Date,
                        DateTime,
                        func,
                        Enum,
                        CheckConstraint)
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.enums import AttendanceEnum, RoleEnum

teacher_group_association = Table(
    "teacher_group_association",
    Base.metadata,
    Column("teachers_id", Integer, ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column("groups_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
)

student_group_association = Table(
    "student_group_association",
    Base.metadata,
    Column("students_id", Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("groups_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
)

teacher_students_association = Table(
    "teacher_students_association",
    Base.metadata,
    Column("teachers_id", Integer, ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column("students_id", Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
)


class Teachers(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    teacher_firstname = Column(String, nullable=False)
    teacher_lastname = Column(String, nullable=False)
    teacher_phone_number = Column(String, nullable=False, unique=True)
    teacher_email = Column(String, unique=True, index=True, nullable=True)

    teacher_subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    teacher_subject = relationship("Subjects", back_populates="subject_teacher")

    attendance = relationship("Attendance", back_populates="teacher")
    teacher_groups = relationship("Groups", secondary=teacher_group_association,
                                  back_populates="group_teachers")  # Ustoz uchun biriktirilgan guruhlar
    teacher_students = relationship("Students", secondary=teacher_students_association,
                                    back_populates="student_teachers")  # Ustoz uchun biriktirilgan studentlar

    teacher_account = relationship("User", back_populates="teacher", uselist=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    student_firstname = Column(String, nullable=False)
    student_lastname = Column(String, nullable=False)
    student_phone_number = Column(String, nullable=False, unique=True)
    student_parents_fullname = Column(String, nullable=False)
    student_parents_phone_number = Column(String, nullable=False)
    student_additional_info = Column(Text)

    student_groups = relationship("Groups", secondary=student_group_association, back_populates="group_students")
    student_attendance = relationship("Attendance", back_populates="student", passive_deletes=True)
    student_payment = relationship("Payments", back_populates="student", passive_deletes=True)
    student_teachers = relationship("Teachers", secondary=teacher_students_association,
                                    back_populates="teacher_students")

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False)
    lesson_time = Column(String, nullable=False)
    lesson_days = Column(ARRAY(String), nullable=False, default=[])

    group_subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    group_subject = relationship("Subjects", back_populates="subject_group")

    attendance = relationship("Attendance", back_populates="group", passive_deletes=True)
    # Guruh ustozi
    group_teachers = relationship("Teachers", secondary=teacher_group_association, back_populates="teacher_groups")
    # Guruh talabalari
    group_students = relationship("Students", secondary=student_group_association, back_populates="student_groups")

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    student = relationship("Students", back_populates="student_payment", passive_deletes=True)

    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    teacher = relationship("Teachers", back_populates="attendance")

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    student = relationship("Students", back_populates="student_attendance", passive_deletes=True)

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    group = relationship("Groups", back_populates="attendance", passive_deletes=True)

    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    subject = relationship("Subjects", back_populates="attendance")

    attendance_date = Column(Date)
    status = Column(
        ENUM(AttendanceEnum, name="attendanceenum", create_type=True),
        nullable=False,
        default=AttendanceEnum.absent.value
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    subject_name = Column(String, nullable=False)

    subject_teacher = relationship("Teachers", back_populates="teacher_subject")
    attendance = relationship("Attendance", back_populates="subject")
    subject_group = relationship("Groups", back_populates="group_subject")

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Admins(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    admin_firstname = Column(String, nullable=False)
    admin_lastname = Column(String, nullable=False)
    admin_phone_number = Column(String, nullable=False)
    admin_email = Column(String, unique=True, index=True, nullable=True)
    admin_additional_info = Column(Text, nullable=True)

    admin_account = relationship("User", back_populates="admin", uselist=False)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_email = Column(String, unique=True, index=True, nullable=True)
    role = Column(
        ENUM(RoleEnum, name="rollenum", create_type=True),
        nullable=False
    )
    refresh_token = Column(String, nullable=True)

    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teachers", back_populates="teacher_account")

    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    admin = relationship("Admins", back_populates="admin_account")



    __table_args__ = (
        CheckConstraint(
            "(teacher_id IS NOT NULL) OR (admin_id IS NOT NULL)",
            name="user_has_role"
        ),
    )
