"""
Database connection and session management.

This module provides the core SQLAlchemy configuration for the Track Tracker
application, including engine creation, session management, and the declarative
base for ORM models.

Usage:
    from app.db.database import SessionLocal, Base, get_db

    # For dependency injection (FastAPI)
    def my_endpoint(db: Session = Depends(get_db)):
        ...

    # For manual session management
    with SessionLocal() as db:
        ...
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session


# Declarative base for ORM models (safe to import without DATABASE_URL)
Base = declarative_base()

# Module-level singletons (lazily initialized)
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _get_database_url() -> str:
    """Get and validate the DATABASE_URL environment variable."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise EnvironmentError(
            "DATABASE_URL environment variable is required. "
            "Expected format: postgresql://user:pass@host:5432/dbname"
        )
    return url


def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy engine (lazy initialization).

    Returns:
        Engine: Configured SQLAlchemy engine with connection pooling
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            _get_database_url(),
            pool_size=5,  # Number of connections to keep open
            max_overflow=10,  # Additional connections allowed beyond pool_size
            pool_timeout=30,  # Seconds to wait for available connection
            pool_recycle=1800,  # Recycle connections after 30 minutes
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create the session factory (lazy initialization).

    Returns:
        sessionmaker: Configured session factory bound to the engine
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


def SessionLocal() -> Session:
    """Create a new database session."""
    return get_session_factory()()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection generator for database sessions.

    Yields a database session and ensures proper cleanup after use.
    Designed for use with FastAPI's Depends() system.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/tracks")
        def get_tracks(db: Session = Depends(get_db)):
            return db.query(Track).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI.

    Provides a database session with automatic commit on success
    and rollback on exception.

    Yields:
        Session: SQLAlchemy database session

    Example:
        with get_db_context() as db:
            db.add(new_track)
            # Commits automatically on exit
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
