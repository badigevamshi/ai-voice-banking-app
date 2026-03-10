from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)

    password = Column(String, nullable=False)

    balance = Column(Float, default=1000.0, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, balance={self.balance})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    sender = Column(String, nullable=False)

    receiver = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Transaction(sender={self.sender}, receiver={self.receiver}, amount={self.amount})>"