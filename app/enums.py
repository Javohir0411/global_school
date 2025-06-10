from enum import Enum

class AttendanceEnum(Enum):
    present = "present"
    absent = "absent"
    late = "late"

class RoleEnum(str, Enum):
    admin = "admin"
    teacher = "teacher"