"""Tests for S3Filesystem abstraction layer.

These tests require a running S3-compatible store (MinIO or AWS S3).
When S3_ENDPOINT_URL is not set, all tests are skipped to avoid
requiring a real S3 connection in CI.
"""

import os
import pytest

from storage.s3 import S3Filesystem


pytestmark = pytest.mark.skipif(
    not os.getenv("S3_ENDPOINT_URL"),
    reason="S3_ENDPOINT_URL not set — skipping S3 integration tests",
)


@pytest.fixture
def s3_fs():
    """Return a real S3Filesystem (requires MinIO or S3_ENDPOINT_URL)."""
    fs = S3Filesystem()
    # Clean up any leftover test objects from previous runs.
    for key in fs.list("test/"):
        fs.delete(key)
    return fs


def test_upload_and_download_bytes(s3_fs):
    """Upload bytes and download them back."""
    remote = "test/hello.txt"
    content = b"hello, s3!"
    s3_fs.upload_bytes(content, remote)
    downloaded = s3_fs.download(remote)
    assert downloaded == content
    s3_fs.delete(remote)


def test_upload_and_download_file(s3_fs, tmp_path):
    """Upload a local file and download it back."""
    remote = "test/file_upload.txt"
    local_src = tmp_path / "source.txt"
    local_src.write_text("file upload test")
    s3_fs.upload(str(local_src), remote)
    local_dst = tmp_path / "downloaded.txt"
    s3_fs.download_to_file(remote, local_dst)
    assert local_dst.read_text() == "file upload test"
    s3_fs.delete(remote)


def test_exists(s3_fs):
    """exists() returns True for existing objects, False otherwise."""
    remote = "test/exists_check.txt"
    assert not s3_fs.exists(remote)
    s3_fs.upload_bytes(b"data", remote)
    assert s3_fs.exists(remote)
    s3_fs.delete(remote)
    assert not s3_fs.exists(remote)


def test_presigned_url(s3_fs):
    """presigned_url() returns a valid HTTP URL."""
    remote = "test/presigned.txt"
    s3_fs.upload_bytes(b"data", remote)
    url = s3_fs.presigned_url(remote)
    assert url.startswith("http")
    s3_fs.delete(remote)


def test_list(s3_fs):
    """list() returns objects under the given prefix."""
    s3_fs.upload_bytes(b"a", "test/list_a.txt")
    s3_fs.upload_bytes(b"b", "test/list_b.txt")
    keys = s3_fs.list("test/")
    assert any("list_a.txt" in k for k in keys)
    assert any("list_b.txt" in k for k in keys)
    s3_fs.delete("test/list_a.txt")
    s3_fs.delete("test/list_b.txt")


def test_delete(s3_fs):
    """delete() removes the object and returns True."""
    remote = "test/delete_me.txt"
    s3_fs.upload_bytes(b"delete me", remote)
    assert s3_fs.exists(remote)
    assert s3_fs.delete(remote) is True
    assert not s3_fs.exists(remote)


def test_delete_nonexistent(s3_fs):
    """delete() returns False for a non-existent object."""
    assert s3_fs.delete("test/does_not_exist.txt") is False