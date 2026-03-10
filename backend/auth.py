from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

import models
import schemas
from database import get_db


router = APIRouter()

# ---------------- JWT CONFIG ----------------

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- PASSWORD FUNCTIONS ----------------

def hash_password(password: str):
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password[:72], hashed_password)


# ---------------- CREATE TOKEN ----------------

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# ---------------- GET CURRENT USER ----------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ---------------- REGISTER ----------------

@router.post("/register")
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    hashed_password = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password=hashed_password,
        balance=1000.0
    )

    try:

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully"
        }

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )


# ---------------- LOGIN ----------------

@router.post("/login")
def login(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="User not found"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )

    access_token = create_access_token(
        data={"sub": db_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }