from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# Database URL (SQLite by default)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bank.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()