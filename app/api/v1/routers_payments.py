from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.schemas import (
    PaymentBase,
    PaymentUpdate,
    PaymentCreate,
    PaymentDetail, PaymentsOutput)
from app.db.crud import (
    create_payment,
    get_payments,
    get_payment,
    update_payment,
    delete_payment)

payment_router = APIRouter()

@payment_router.post("/payments")
def add_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, data)

@payment_router.get("/payments", response_model=List[PaymentsOutput])
def read_payments(db: Session = Depends(get_db)):
    return get_payments(db)

@payment_router.get("/payments/{payment_id}", response_model=PaymentDetail)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")
    return payment

@payment_router.put("/payments/{payment_id}")
def modify_payment(payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    return update_payment(db, payment_id, data)

@payment_router.delete("/payments/{payment_id}")
def remove_payment(payment_id: int, db: Session = Depends(get_db)):
    return delete_payment(db, payment_id)