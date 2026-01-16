"""
Database model and query tests with in-memory SQLite.

Tests database operations using an in-memory SQLite database
instead of the real PostgreSQL instance.

Usage:
    uv run python -m pytest tests/test_db.py
    uv run python -m tests.test_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Track, TrackSnapshot
from app.db.query import (
    get_track_count,
    get_snapshot_count,
    get_top_tracks,
    get_recent_snapshots,
)


def get_test_session():
    """Create an in-memory SQLite database and return a session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_track_model() -> None:
    """Test Track model creation and attributes."""
    db = get_test_session()

    track = Track(
        id="test123",
        name="Test Track",
        artist="Test Artist",
        album="Test Album",
        popularity=75,
    )
    db.add(track)
    db.commit()

    # Query it back
    retrieved = db.query(Track).filter(Track.id == "test123").first()

    assert retrieved is not None
    assert retrieved.name == "Test Track"
    assert retrieved.artist == "Test Artist"
    assert retrieved.album == "Test Album"
    assert retrieved.popularity == 75
    assert retrieved.first_seen is not None

    db.close()


def test_track_snapshot_model() -> None:
    """Test TrackSnapshot model and relationship to Track."""
    db = get_test_session()

    # Create track first
    track = Track(id="test123", name="Test Track", artist="Test Artist", popularity=75)
    db.add(track)
    db.commit()

    # Create snapshot
    snapshot = TrackSnapshot(track_id="test123", popularity=75)
    db.add(snapshot)
    db.commit()

    # Query snapshot and verify relationship
    retrieved = db.query(TrackSnapshot).first()

    assert retrieved is not None
    assert retrieved.track_id == "test123"
    assert retrieved.popularity == 75
    assert retrieved.timestamp is not None
    assert retrieved.track.name == "Test Track"  # Relationship works

    db.close()


def test_track_merge_upsert() -> None:
    """Test that merge() properly upserts tracks."""
    db = get_test_session()

    # Insert initial track
    track1 = Track(
        id="test123", name="Original Name", artist="Test Artist", popularity=50
    )
    db.merge(track1)
    db.commit()

    # Upsert with same ID but different data
    track2 = Track(
        id="test123", name="Updated Name", artist="Test Artist", popularity=75
    )
    db.merge(track2)
    db.commit()

    # Should only have one track with updated values
    tracks = db.query(Track).all()
    assert len(tracks) == 1
    assert tracks[0].name == "Updated Name"
    assert tracks[0].popularity == 75

    db.close()


def test_get_track_count() -> None:
    """Test track count query."""
    db = get_test_session()

    assert get_track_count(db) == 0

    db.add(Track(id="t1", name="Track 1", artist="Artist"))
    db.add(Track(id="t2", name="Track 2", artist="Artist"))
    db.commit()

    assert get_track_count(db) == 2

    db.close()


def test_get_top_tracks() -> None:
    """Test top tracks query orders by popularity."""
    db = get_test_session()

    db.add(Track(id="t1", name="Low Pop", artist="Artist", popularity=25))
    db.add(Track(id="t2", name="High Pop", artist="Artist", popularity=90))
    db.add(Track(id="t3", name="Mid Pop", artist="Artist", popularity=50))
    db.commit()

    top = get_top_tracks(db, limit=2)

    assert len(top) == 2
    assert top[0].name == "High Pop"
    assert top[1].name == "Mid Pop"

    db.close()


def test_get_recent_snapshots() -> None:
    """Test recent snapshots query with eager loading."""
    db = get_test_session()

    # Create track
    db.add(Track(id="t1", name="Track", artist="Artist"))
    db.commit()

    # Create snapshots
    db.add(TrackSnapshot(track_id="t1", popularity=50))
    db.add(TrackSnapshot(track_id="t1", popularity=60))
    db.commit()

    recent = get_recent_snapshots(db, limit=2)

    assert len(recent) == 2
    # Verify relationship is loaded (no additional query)
    assert recent[0].track.name == "Track"

    db.close()


def test_cascade_delete() -> None:
    """Test that deleting a track cascades to snapshots."""
    db = get_test_session()

    track = Track(id="t1", name="Track", artist="Artist")
    db.add(track)
    db.commit()

    db.add(TrackSnapshot(track_id="t1", popularity=50))
    db.add(TrackSnapshot(track_id="t1", popularity=60))
    db.commit()

    assert get_snapshot_count(db) == 2

    # Delete track
    db.delete(track)
    db.commit()

    # Snapshots should be deleted too
    assert get_snapshot_count(db) == 0

    db.close()


def run_tests() -> None:
    """Run all database tests."""
    print("Running database tests (in-memory SQLite)...\n")

    print("1. test_track_model: ", end="")
    test_track_model()
    print("OK")

    print("2. test_track_snapshot_model: ", end="")
    test_track_snapshot_model()
    print("OK")

    print("3. test_track_merge_upsert: ", end="")
    test_track_merge_upsert()
    print("OK")

    print("4. test_get_track_count: ", end="")
    test_get_track_count()
    print("OK")

    print("5. test_get_top_tracks: ", end="")
    test_get_top_tracks()
    print("OK")

    print("6. test_get_recent_snapshots: ", end="")
    test_get_recent_snapshots()
    print("OK")

    print("7. test_cascade_delete: ", end="")
    test_cascade_delete()
    print("OK")

    print("\nAll database tests passed!")


if __name__ == "__main__":
    run_tests()
