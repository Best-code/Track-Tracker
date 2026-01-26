"""Configuration settings for the Track Tracker API."""

APP_CONFIG = {
    "title": "Track Tracker API",
    "description": "API for tracking Spotify track metrics over time",
    "version": "0.1.0",
}

CORS_CONFIG = {
    "allow_origins": [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
