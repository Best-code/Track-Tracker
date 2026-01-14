"""
Spotify API integration module.

Provides authenticated access to the Spotify Web API and ingestion
pipelines for collecting track data.

Main exports:
    get_spotify_client: Create authenticated Spotify client
    ingest_new_releases: Fetch and store new release data
"""

from app.ingestion.spotify.ingest_to_db import (
    get_spotify_client,
    ingest_new_releases,
    IngestionResult,
)

__all__ = [
    "get_spotify_client",
    "ingest_new_releases",
    "IngestionResult",
]
