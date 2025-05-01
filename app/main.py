from fastapi import FastAPI, Request
from app.api.v1.routers_teachers import teacher_router as teacher
from app.api.v1.routers_students import student_routers as student
app = FastAPI(title="My Project API", version="1.0")

routers = [
    (teacher, "Teachers"),
    (student, "Students")
]

for router, tag in routers:
    app.include_router(router, prefix="/api/v1", tags=[tag])

@app.get("/")
def main_page():
    return "MAIN PAGE OF GLOBAL SCHOOL ADMIN PANEL "

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)