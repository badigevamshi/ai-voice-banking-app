from pydantic import BaseModel
from datetime import datetime


# ---------------- USER ----------------

class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    balance: float

    class Config:
        from_attributes = True


# ---------------- MONEY TRANSFER ----------------

class TransferRequest(BaseModel):
    receiver: str
    amount: float


# ---------------- TRANSACTION RESPONSE ----------------

class TransactionResponse(BaseModel):
    sender: str
    receiver: str
    amount: float
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------------- VOICE COMMAND ----------------

class VoiceCommand(BaseModel):
    text: str