from fastapi import FastAPI, Request
from app.api.v1.routers_teachers import teacher_router as teacher
from app.api.v1.routers_students import student_router as student
from app.api.v1.routers_groups import groups_router as group
from app.api.v1.routers_attendance import attendance_router as attendance
from app.api.v1.routers_payments import payment_router as payment
from app.api.v1.routers_subjects import subject_router as subject
from app.api.v1.router_admins import admin_router as admin
from app.api.v1.router_user import user_router as user
from app.api.v1.router_authentication import authentication_router as registration
app = FastAPI(title="My Project API", version="1.0")

routers = [
    (subject, "Subject"),
    (group, "Groups"),
    (teacher, "Teachers"),
    (student, "Students"),
    (attendance, "Attendance"),
    (payment, "Payment"),
    (admin, "Admin"),
    (user, "User"),
    (registration, "Registration")
]

for router, tag in routers:
    app.include_router(router, prefix="/api/v1", tags=[tag])

@app.get("/")
def main_page():
    return "MAIN PAGE OF GLOBAL SCHOOL ADMIN PANEL "

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)