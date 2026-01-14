"""
AWS S3 integration module.

Provides utilities for storing and retrieving raw data from S3.
Used to persist API responses before processing.

Main exports:
    get_s3_client: Create S3 client
    upload_json: Upload dictionary as JSON
    download_json: Download and parse JSON
    list_objects: List bucket contents
"""

from app.ingestion.s3.client import (
    get_s3_client,
    upload_json,
    download_json,
    list_objects,
)

__all__ = [
    "get_s3_client",
    "upload_json",
    "download_json",
    "list_objects",
]
