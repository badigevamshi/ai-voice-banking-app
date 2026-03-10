from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import re

import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter()


@router.post("/voice-command")
def process_voice(
    command: schemas.VoiceCommand,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    text = command.text.lower().strip()

    # ---------------- BALANCE ----------------

    balance_keywords = [
        "balance",
        "account balance",
        "bank balance",
        "how much money",
        "money in account"
    ]

    if any(word in text for word in balance_keywords):

        return {
            "intent": "check_balance",
            "balance": current_user.balance,
            "message": f"Your account balance is {current_user.balance} rupees"
        }

    # ---------------- SEND MONEY ----------------

    send_keywords = ["send", "transfer", "pay", "give"]

    if any(word in text for word in send_keywords):

        amount_match = re.search(r"(\d+(\.\d+)?)", text)
        receiver_match = re.search(r"to\s+([a-zA-Z0-9_]+)", text)

        if not amount_match:
            raise HTTPException(status_code=400, detail="Amount not found in command")

        if not receiver_match:
            raise HTTPException(status_code=400, detail="Receiver name not found")

        amount = float(amount_match.group(1))
        receiver_name = receiver_match.group(1).lower()

        receiver = db.query(models.User).filter(
            func.lower(models.User.username) == receiver_name
        ).first()

        if receiver is None:
            raise HTTPException(status_code=404, detail="Receiver not found")

        if receiver.username == current_user.username:
            raise HTTPException(status_code=400, detail="You cannot send money to yourself")

        if current_user.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        current_user.balance -= amount
        receiver.balance += amount

        txn = models.Transaction(
            sender=current_user.username,
            receiver=receiver.username,
            amount=amount
        )

        db.add(txn)
        db.commit()
        db.refresh(txn)

        return {
            "intent": "send_money",
            "message": f"{amount} rupees sent to {receiver.username}",
            "balance": current_user.balance
        }

    # ---------------- TRANSACTION HISTORY ----------------

    history_keywords = [
        "transaction",
        "transactions",
        "history",
        "payment history"
    ]

    if any(word in text for word in history_keywords):

        transactions = db.query(models.Transaction).filter(
            or_(
                models.Transaction.sender == current_user.username,
                models.Transaction.receiver == current_user.username
            )
        ).order_by(models.Transaction.id.desc()).limit(5).all()

        if not transactions:
            return {
                "intent": "transaction_history",
                "message": "No transactions found"
            }

        history_list = []

        for txn in transactions:
            history_list.append({
                "sender": txn.sender,
                "receiver": txn.receiver,
                "amount": txn.amount
            })

        return {
            "intent": "transaction_history",
            "transactions": history_list
        }

    # ---------------- UNKNOWN COMMAND ----------------

    return {
        "intent": "unknown",
        "message": "Sorry, I did not understand your request"
    }