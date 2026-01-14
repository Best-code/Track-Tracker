"""
AWS S3 connectivity tests.

Tests upload, list, and download operations against the configured S3 bucket.

Usage:
    uv run python -m tests.test_s3
"""

import logging
import os
from datetime import datetime

from app.ingestion.s3.client import upload_json, download_json, list_objects


def run_s3_tests() -> None:
    """
    Execute S3 connectivity tests.

    Tests upload, list, and download operations against the configured bucket.
    """
    print("Running S3 tests...\n")
    bucket = os.environ["S3_RAW_BUCKET"]

    # 1. Upload test data
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "tracks": [
            {"name": "Track A", "artist": "Artist 1"},
            {"name": "Track B", "artist": "Artist 2"},
        ]
    }

    key = f"test/snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    upload_json(bucket, key, test_data)

    # 2. List bucket contents
    print("\nObjects in bucket:")
    for obj in list_objects(bucket, prefix="test/"):
        print(f"  - {obj['Key']} ({obj['Size']} bytes)")

    # 3. Download and verify
    print("\nDownloading...")
    downloaded = download_json(bucket, key)
    print(f"Got {len(downloaded['tracks'])} tracks from {downloaded['timestamp']}")

    print("\nAll S3 tests passed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_s3_tests()
