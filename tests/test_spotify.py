"""
Spotify ingestion tests with mocked API.

Tests the Spotify ingestion pipeline without hitting the real API.

Usage:
    uv run python -m pytest tests/test_spotify.py
    uv run python -m tests.test_spotify
"""

from unittest.mock import Mock, patch

from app.ingestion.spotify.spotify_to_db import (
    get_spotify_client,
    ingest_new_releases,
    IngestionResult,
)


# Sample mock data matching Spotify API response structure
MOCK_TRACK = {
    "id": "track123",
    "name": "Test Track",
    "artists": [{"name": "Test Artist"}],
    "popularity": 75,
}

MOCK_ALBUM = {
    "id": "album123",
    "name": "Test Album",
}

MOCK_NEW_RELEASES = {
    "albums": {
        "items": [
            {"id": "album123", "name": "Test Album"},
            {"id": "album456", "name": "Another Album"},
        ]
    }
}

MOCK_ALBUM_TRACKS = {
    "items": [
        {"id": "track123", "name": "Test Track"},
        {"id": "track456", "name": "Another Track"},
    ]
}


def test_get_spotify_client() -> None:
    """Test that Spotify client is created with correct credentials."""
    with (
        patch(
            "app.ingestion.spotify.spotify_to_db.SpotifyClientCredentials"
        ) as mock_creds,
        patch("app.ingestion.spotify.spotify_to_db.spotipy.Spotify") as mock_spotify,
        patch.dict(
            "os.environ",
            {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"},
        ),
    ):
        client = get_spotify_client()
        client

        mock_creds.assert_called_once_with(
            client_id="test_id", client_secret="test_secret"
        )
        mock_spotify.assert_called_once()


def test_ingest_new_releases() -> None:
    """Test ingestion pipeline with mocked Spotify API and database."""
    mock_spotify = Mock()
    mock_spotify.new_releases.return_value = MOCK_NEW_RELEASES
    mock_spotify.album_tracks.return_value = MOCK_ALBUM_TRACKS
    mock_spotify.track.return_value = MOCK_TRACK

    with (
        patch(
            "app.ingestion.spotify.spotify_to_db.get_spotify_client",
            return_value=mock_spotify,
        ),
        patch("app.ingestion.spotify.spotify_to_db.get_db_context") as mock_db_context,
    ):
        # Setup mock database session
        mock_session = Mock()
        mock_db_context.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_context.return_value.__exit__ = Mock(return_value=False)

        result = ingest_new_releases(limit=2)

        # Verify API was called correctly
        mock_spotify.new_releases.assert_called_once_with(limit=2)
        assert mock_spotify.album_tracks.call_count == 2  # Two albums
        assert mock_spotify.track.call_count == 4  # Two tracks per album

        # Verify result
        assert isinstance(result, IngestionResult)
        assert result.tracks_processed == 4
        assert result.snapshots_created == 4
        assert result.errors == 0


def test_ingest_handles_api_errors() -> None:
    """Test that ingestion handles API errors gracefully."""
    mock_spotify = Mock()
    mock_spotify.new_releases.return_value = MOCK_NEW_RELEASES
    mock_spotify.album_tracks.side_effect = Exception("API Error")

    with (
        patch(
            "app.ingestion.spotify.spotify_to_db.get_spotify_client",
            return_value=mock_spotify,
        ),
        patch("app.ingestion.spotify.spotify_to_db.get_db_context") as mock_db_context,
    ):
        mock_session = Mock()
        mock_db_context.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_context.return_value.__exit__ = Mock(return_value=False)

        result = ingest_new_releases(limit=2)

        # Should have errors but not crash
        assert result.errors == 2  # Both albums failed
        assert result.tracks_processed == 0


def run_tests() -> None:
    """Run all Spotify tests."""
    print("Running Spotify tests (mocked)...\n")

    print("1. test_get_spotify_client: ", end="")
    test_get_spotify_client()
    print("OK")

    print("2. test_ingest_new_releases: ", end="")
    test_ingest_new_releases()
    print("OK")

    print("3. test_ingest_handles_api_errors: ", end="")
    test_ingest_handles_api_errors()
    print("OK")

    print("\nAll Spotify tests passed!")


if __name__ == "__main__":
    run_tests()
