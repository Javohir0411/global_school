from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.crud import (
    create_attendance,
    get_attendances,
    get_attendance,
    update_attendance,
    delete_attendance)

from app.db.schemas import AttendanceCreate, AttendanceDetail, AttendanceBase, AttendanceUpdate, AttendancesOutput

attendance_router = APIRouter()

@attendance_router.post("/attendances", response_model=dict)
def add_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    return create_attendance(db, data)

@attendance_router.get("/attendances", response_model=List[AttendancesOutput])
def read_attendances(db: Session = Depends(get_db)):
    return get_attendances(db)

@attendance_router.get("/attendances/{attendance_id}", response_model=AttendanceDetail)
def read_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = get_attendance(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance

@attendance_router.put("/attendances/{attendance_id}")
def modify_attendance(data: AttendanceUpdate, attendance_id: int, db: Session = Depends(get_db)):
    return update_attendance(db, attendance_id, data)

@attendance_router.delete("/attendances/{attendance_id}")
def remove_attendance(attendance_id: int, db: Session = Depends(get_db)):
    return delete_attendance(db, attendance_id)
