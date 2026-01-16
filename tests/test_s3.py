"""
AWS S3 client tests with mocked boto3.

Tests S3 upload, list, and download operations without hitting real AWS.

Usage:
    uv run python -m pytest tests/test_s3.py
    uv run python -m tests.test_s3
"""

import json
from unittest.mock import Mock, patch

from app.ingestion.s3.client import (
    get_s3_client,
    upload_json,
    download_json,
    list_objects,
)


def test_get_s3_client() -> None:
    """Test S3 client creation with correct region."""
    with (
        patch("app.ingestion.s3.client.boto3.client") as mock_boto_client,
        patch.dict("os.environ", {"AWS_REGION": "us-west-2"}),
    ):
        client = get_s3_client()
        client

        mock_boto_client.assert_called_once_with("s3", region_name="us-west-2")


def test_get_s3_client_default_region() -> None:
    """Test S3 client uses default region when not specified."""
    with (
        patch("app.ingestion.s3.client.boto3.client") as mock_boto_client,
        patch.dict("os.environ", {}, clear=True),
    ):
        client = get_s3_client()
        client

        mock_boto_client.assert_called_once_with("s3", region_name="us-east-1")


def test_upload_json() -> None:
    """Test uploading JSON data to S3."""
    mock_s3 = Mock()

    with patch("app.ingestion.s3.client.get_s3_client", return_value=mock_s3):
        test_data = {"key": "value", "number": 42}
        upload_json("test-bucket", "path/to/file.json", test_data)

        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args

        assert call_args.kwargs["Bucket"] == "test-bucket"
        assert call_args.kwargs["Key"] == "path/to/file.json"
        assert call_args.kwargs["ContentType"] == "application/json"

        # Verify JSON content is correct
        uploaded_body = call_args.kwargs["Body"]
        parsed = json.loads(uploaded_body)
        assert parsed == test_data


def test_download_json() -> None:
    """Test downloading and parsing JSON from S3."""
    mock_s3 = Mock()
    test_data = {"tracks": [{"name": "Track A"}], "count": 1}

    # Mock the S3 response body
    mock_body = Mock()
    mock_body.read.return_value = json.dumps(test_data).encode("utf-8")
    mock_s3.get_object.return_value = {"Body": mock_body}

    with patch("app.ingestion.s3.client.get_s3_client", return_value=mock_s3):
        result = download_json("test-bucket", "path/to/file.json")

        mock_s3.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="path/to/file.json"
        )
        assert result == test_data


def test_list_objects() -> None:
    """Test listing objects in S3 bucket."""
    mock_s3 = Mock()
    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "test/file1.json", "Size": 100},
            {"Key": "test/file2.json", "Size": 200},
        ]
    }

    with patch("app.ingestion.s3.client.get_s3_client", return_value=mock_s3):
        result = list_objects("test-bucket", prefix="test/")

        mock_s3.list_objects_v2.assert_called_once_with(
            Bucket="test-bucket", Prefix="test/"
        )
        assert len(result) == 2
        assert result[0]["Key"] == "test/file1.json"


def test_list_objects_empty_bucket() -> None:
    """Test listing objects returns empty list for empty bucket."""
    mock_s3 = Mock()
    mock_s3.list_objects_v2.return_value = {}  # No "Contents" key

    with patch("app.ingestion.s3.client.get_s3_client", return_value=mock_s3):
        result = list_objects("test-bucket")

        assert result == []


def run_tests() -> None:
    """Run all S3 tests."""
    print("Running S3 tests (mocked)...\n")

    print("1. test_get_s3_client: ", end="")
    test_get_s3_client()
    print("OK")

    print("2. test_get_s3_client_default_region: ", end="")
    test_get_s3_client_default_region()
    print("OK")

    print("3. test_upload_json: ", end="")
    test_upload_json()
    print("OK")

    print("4. test_download_json: ", end="")
    test_download_json()
    print("OK")

    print("5. test_list_objects: ", end="")
    test_list_objects()
    print("OK")

    print("6. test_list_objects_empty_bucket: ", end="")
    test_list_objects_empty_bucket()
    print("OK")

    print("\nAll S3 tests passed!")


if __name__ == "__main__":
    run_tests()
