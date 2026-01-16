"""
Track Tracker test suite.

All tests use mocks to avoid hitting real APIs or databases:
- test_db.py: Uses in-memory SQLite instead of PostgreSQL
- test_spotify.py: Mocks Spotify API responses
- test_s3.py: Mocks boto3 S3 client

Usage:
    # Run all tests with pytest
    uv run python -m pytest tests/

    # Run individual test modules directly
    uv run python -m tests.test_db
    uv run python -m tests.test_spotify
    uv run python -m tests.test_s3

    # Run with verbose output
    uv run python -m pytest tests/ -v
"""
