from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter()


# ---------------- SEND MONEY ----------------

@router.post("/send")
def send_money(
    txn: schemas.TransferRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    sender = current_user

    receiver = db.query(models.User).filter(
        func.lower(models.User.username) == txn.receiver.lower()
    ).first()

    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if receiver.username.lower() == sender.username.lower():
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")

    if txn.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    if sender.balance < txn.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    sender.balance -= txn.amount
    receiver.balance += txn.amount

    transaction = models.Transaction(
        sender=sender.username,
        receiver=receiver.username,
        amount=txn.amount
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "intent": "send_money",
        "message": f"{txn.amount} rupees sent to {receiver.username}",
        "sender_balance": sender.balance
    }


# ---------------- TRANSACTION HISTORY ----------------

@router.get("/")
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        or_(
            models.Transaction.sender == current_user.username,
            models.Transaction.receiver == current_user.username
        )
    ).order_by(models.Transaction.id.desc()).all()

    history = []

    for txn in transactions:
        history.append({
            "sender": txn.sender,
            "receiver": txn.receiver,
            "amount": txn.amount,
            "timestamp": txn.timestamp
        })

    return {
        "intent": "transaction_history",
        "transactions": history
    }