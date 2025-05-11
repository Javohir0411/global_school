from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.schemas import SubjectCreate, SubjectDetail, SubjectBase, SubjectResponse
from app.db.crud import (
    create_subject,
    get_subjects,
    get_subject_by_id,
    update_subject,
    delete_subject)

subject_router = APIRouter()

@subject_router.post("/subjects")
def add_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    return create_subject(db, data)

@subject_router.get("/subjects")
def read_subjects(db: Session = Depends(get_db)):
    return get_subjects(db)

@subject_router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    return get_subject_by_id(db, subject_id)

@subject_router.put("/subjects/{subject_id}")
def modify_subject(subject_id: int, data: SubjectCreate, db: Session = Depends(get_db)):
    return update_subject(db, subject_id, data)

@subject_router.delete("/subjects/{subject_id}")
def remove_subject(subject_id: int, db: Session = Depends(get_db)):
    return delete_subject(db, subject_id)