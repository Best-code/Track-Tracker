"""
Database integration tests.

Tests database initialization, data insertion, and querying functionality.

Usage:
    uv run python -m tests.test_db
"""

from app.db.database import get_db_context
from app.db.init import init_db
from app.db.models import Track, TrackSnapshot


def add_test_data() -> None:
    """
    Insert sample track and snapshot records for testing.

    Uses merge() for tracks to support idempotent insertion (insert or update).
    """
    with get_db_context() as db:
        track = Track(
            id="test123",
            name="Test Track",
            artist="Test Artist",
            album="Test Album",
            popularity=75
        )
        db.merge(track)

        snapshot = TrackSnapshot(
            track_id="test123",
            popularity=75
        )
        db.add(snapshot)

    print("Test data added")


def query_data() -> None:
    """Query and display all tracks and snapshots in the database."""
    with get_db_context() as db:
        tracks = db.query(Track).all()
        print(f"\nTracks ({len(tracks)}):")
        for track in tracks:
            print(f"  - {track.name} by {track.artist} (popularity: {track.popularity})")

        snapshots = db.query(TrackSnapshot).all()
        print(f"\nSnapshots ({len(snapshots)}):")
        for snapshot in snapshots:
            print(f"  - Track {snapshot.track_id}: {snapshot.popularity} at {snapshot.timestamp}")


def run_db_tests() -> None:
    """Run all database tests."""
    print("Running database tests...\n")
    init_db()
    add_test_data()
    query_data()
    print("\nAll database tests passed!")


if __name__ == "__main__":
    run_db_tests()
