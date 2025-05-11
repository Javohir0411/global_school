from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.schemas import GroupBase, GroupDetail, GroupUpdate, GroupCreate, GroupOutput
from app.db.crud import (
    create_group,
    get_groups,
    get_group,
    update_group,
    delete_group)

groups_router = APIRouter()


@groups_router.post("/groups")
def add_groups(data: GroupCreate, db: Session = Depends(get_db)):
    return create_group(db, data)


@groups_router.get("/groups", response_model=List[GroupOutput])
def read_groups(db: Session = Depends(get_db)):
    return get_groups(db)


@groups_router.get("/groups/{group_id}", response_model=GroupDetail)
def read_group(group_id: int, db: Session = Depends(get_db)):
    return get_group(db, group_id)


@groups_router.put("/groups/{group_id}")
def modify_group(data: GroupUpdate, group_id: int, db: Session = Depends(get_db)):
    return update_group(db, group_id, data)


@groups_router.delete("/groups/{group_id}")
def remove_group(group_id: int, db: Session = Depends(get_db)):
    return delete_group(db, group_id)
