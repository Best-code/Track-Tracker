"""
SQLAlchemy ORM models for the Track Tracker database.

This module defines the core data models:
- Track: Master record for each unique track across platforms
- TrackSnapshot: Time-series popularity data for trend analysis

The snapshot pattern enables historical tracking of popularity metrics,
which is essential for identifying emerging tracks before they chart.
"""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped

from app.db.database import Base


class Track(Base):
    """
    Master record for a music track.

    Stores canonical track information and maintains links to all
    historical popularity snapshots. Uses Spotify track ID as primary key.

    Attributes:
        id: Spotify track ID (primary key)
        name: Track title
        artist: Primary artist name
        album: Album name (optional for singles)
        popularity: Current Spotify popularity score (0-100)
        first_seen: When this track was first ingested
        last_updated: When this track was last updated

    Relationships:
        snapshots: Historical popularity records for this track
    """

    __tablename__ = "tracks"
    __table_args__ = (
        Index("ix_tracks_popularity", "popularity"),
        Index("ix_tracks_artist", "artist"),
        Index("ix_tracks_first_seen", "first_seen"),
    )

    id: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String(500), nullable=False)
    artist: Mapped[str] = Column(String(500), nullable=False)
    album: Mapped[Optional[str]] = Column(String(500))
    popularity: Mapped[Optional[int]] = Column(Integer)
    first_seen: Mapped[datetime] = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_updated: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to snapshots
    snapshots: Mapped[List["TrackSnapshot"]] = relationship(
        "TrackSnapshot", back_populates="track", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Track(id={self.id!r}, name={self.name!r}, artist={self.artist!r})>"


class TrackSnapshot(Base):
    """
    Point-in-time popularity snapshot for a track.

    Captures popularity metrics at regular intervals to enable
    trend analysis and early detection of rising tracks.

    Attributes:
        id: Auto-incrementing primary key
        track_id: Foreign key to parent Track
        popularity: Spotify popularity score at snapshot time (0-100)
        timestamp: When this snapshot was captured

    Relationships:
        track: Parent Track record
    """

    __tablename__ = "track_snapshots"
    __table_args__ = (
        Index("ix_snapshots_track_timestamp", "track_id", "timestamp"),
        Index("ix_snapshots_timestamp", "timestamp"),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[str] = Column(
        String, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False
    )
    popularity: Mapped[Optional[int]] = Column(Integer)
    timestamp: Mapped[datetime] = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to parent track
    track: Mapped["Track"] = relationship("Track", back_populates="snapshots")

    def __repr__(self) -> str:
        return f"<TrackSnapshot(track_id={self.track_id!r}, popularity={self.popularity}, timestamp={self.timestamp})>"
