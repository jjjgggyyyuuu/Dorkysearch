from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import stripe
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from .database import SessionLocal, engine
from . import models, schemas, crud
from .routers import dorks, osint, auth, payments
from .core.config import settings

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI(
    title="DorkySearch API",
    description="API for DorkySearch.com - Advanced OSINT and Google Dorking Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dorks.router, prefix="/api/dorks", tags=["Google Dorks"])
app.include_router(osint.router, prefix="/api/osint", tags=["OSINT"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {
        "message": "Welcome to DorkySearch API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# Initialize database
models.Base.metadata.create_all(bind=engine) 