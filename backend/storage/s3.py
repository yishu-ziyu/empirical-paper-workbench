"""S3-compatible object storage abstraction.

Provides a unified interface for reading/writing files to S3 or
S3-compatible stores (MinIO, AWS S3, Alibaba OSS, etc.).

Local development uses MinIO; production uses the configured endpoint.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from config import settings


class S3Filesystem:
    """Thin wrapper around boto3 for S3-compatible object storage.

    Usage:
        fs = S3Filesystem()
        fs.upload("local.csv", "remote/path/file.csv")
        content = fs.download("remote/path/file.csv")
        url = fs.presigned_url("remote/path/file.csv", expires=3600)
    """

    def __init__(self) -> None:
        self._client = None  # lazy init
        self._bucket = settings.S3_BUCKET

    @property
    def client(self):
        if self._client is None:
            kwargs: dict = {
                "service_name": "s3",
                "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
            }
            if settings.S3_ENDPOINT_URL:
                kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
                # MinIO requires path-style addressing
                kwargs["config"] = Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                    connect_timeout=10,
                    read_timeout=30,
                )
            else:
                kwargs["config"] = Config(
                    signature_version="s3v4",
                    connect_timeout=10,
                    read_timeout=30,
                )
            if settings.S3_REGION:
                kwargs["region_name"] = settings.S3_REGION
            self._client = boto3.client(**kwargs)
            self._ensure_bucket()
        return self._client

    def _ensure_bucket(self) -> None:
        """Create the bucket if it does not exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def _key(self, path: str) -> str:
        """Prefix the path with S3_PATH_PREFIX (acts as virtual folder)."""
        prefix = settings.S3_PATH_PREFIX.rstrip("/")
        return f"{prefix}/{path.lstrip('/')}"

    def upload(self, local_path: str | Path, remote_path: str) -> str:
        """Upload a local file to S3. Returns the remote key."""
        key = self._key(remote_path)
        self.client.upload_file(str(local_path), self._bucket, key)
        return key

    def upload_bytes(self, data: bytes, remote_path: str) -> str:
        """Upload bytes directly to S3. Returns the remote key."""
        key = self._key(remote_path)
        self.client.put_object(Bucket=self._bucket, Key=key, Body=data)
        return key

    def download(self, remote_path: str) -> bytes:
        """Download a file from S3 as bytes."""
        key = self._key(remote_path)
        buf = io.BytesIO()
        self.client.download_fileobj(self._bucket, key, buf)
        buf.seek(0)
        return buf.read()

    def download_to_file(self, remote_path: str, local_path: str | Path) -> Path:
        """Download an S3 object to a local file. Returns the local path."""
        key = self._key(remote_path)
        local = Path(local_path)
        local.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self._bucket, key, str(local))
        return local

    def presigned_url(self, remote_path: str, expires: int = 3600) -> str:
        """Generate a presigned download URL (default: 1 hour)."""
        key = self._key(remote_path)
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires,
        )

    def delete(self, remote_path: str) -> bool:
        """Delete an object from S3. Returns True if successful."""
        key = self._key(remote_path)
        try:
            self.client.delete_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def exists(self, remote_path: str) -> bool:
        """Check if an object exists in S3."""
        key = self._key(remote_path)
        try:
            self.client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def list(self, prefix: str = "") -> list[str]:
        """List objects under the given prefix."""
        key_prefix = self._key(prefix) if prefix else settings.S3_PATH_PREFIX
        response = self.client.list_objects_v2(
            Bucket=self._bucket, Prefix=key_prefix
        )
        return [
            obj["Key"]
            for obj in response.get("Contents", [])
        ]


# Module-level singleton
s3_fs = S3Filesystem()