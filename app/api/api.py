"""
FastAPI application for Track Tracker.

This module provides REST API endpoints for accessing track data.

Run with:
    uvicorn app.api.api:app --reload
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .models import UserInDB

fake_users_db = {
    "colinm": {
        "username": "colinm",
        "full_name": "Colin Maloney",
        "email": "cpm22h@fsu.edu",
        "hashed_password": "password",
        "disabled": False,
    },
}

# Create FastAPI app instance
app = FastAPI(
    title="Track Tracker API",
    description="API for tracking Spotify track metrics over time",
    version="0.1.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# CORS middleware - allows frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Track Tracker API is running"}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = form_data.password
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
