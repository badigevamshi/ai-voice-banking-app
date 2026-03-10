from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine

from auth import router as auth_router
from transactions import router as txn_router
from voice import router as voice_router


# ---------------- DATABASE SETUP ----------------

models.Base.metadata.create_all(bind=engine)


# ---------------- FASTAPI APP ----------------

app = FastAPI(
    title="Finora AI Voice Banking API",
    description="Backend API for AI Voice Banking System",
    version="1.0.0"
)


# ---------------- CORS CONFIGURATION ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROOT ENDPOINT ----------------

@app.get("/")
def home():
    return {
        "message": "Finora AI Voice Banking API is running"
    }


# ---------------- ROUTERS ----------------

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    txn_router,
    prefix="/transactions",
    tags=["Transactions"]
)

app.include_router(
    voice_router,
    prefix="/voice",
    tags=["Voice Banking"]
)