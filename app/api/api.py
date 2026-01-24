"""
FastAPI application for Track Tracker.

This module provides REST API endpoints for accessing track data.

Run with:
    uvicorn app.api.api:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="Track Tracker API",
    description="API for tracking Spotify track metrics over time",
    version="0.1.0",
)

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
