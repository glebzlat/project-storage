import logging

import boto3
from botocore.exceptions import ClientError

from project_storage.core.config import settings


_logger = logging.getLogger("file_storage")


class S3Client:
    """Wrapper around boto3 S3 client for file storage operations"""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self._bucket = settings.AWS_S3_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
            _logger.debug("Bucket exists: %s", self._bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ("404", "NoSuchBucket", "404 Not Found"):
                _logger.info("Bucket %s not found, creating...", self._bucket)
                try:
                    self._client.create_bucket(Bucket=self._bucket)
                    _logger.info("Created bucket: %s", self._bucket)
                except ClientError as create_err:
                    _logger.error(
                        "Failed to create bucket %s: %s",
                        self._bucket,
                        create_err
                    )
                    raise
            else:
                _logger.error(
                    "Failed to check bucket %s: %s", self._bucket, e
                )
                raise

    def upload_fileobj(
        self,
        file_obj,
        key: str,
        content_type: str | None = None
    ) -> None:
        """Upload a file-like object to S3

        Args:
            file_obj: File-like object (BytesIO, file handle, etc.)
            key: S3 object key (storage path)
            content_type: Optional MIME type for the object

        Raises:
            ClientError: If upload fails.
        """
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            _logger.debug(
                "Uploading file: storage_key=%s content_type=%s",
                key, content_type
            )

            self._client.upload_fileobj(
                file_obj,
                self._bucket,
                key,
                ExtraArgs=extra_args if extra_args else None,
            )
            _logger.info("Uploaded file to S3: key=%s", key)
        except ClientError as e:
            _logger.error(
                "Failed to upload file to S3: key=%s, error=%s", key, e)
            raise

    def download_fileobj(self, key: str, file_obj) -> None:
        """Download an S3 object into a file-like object

        Args:
            key: S3 object key
            file_obj: File-like object to write into

        Raises:
            ClientError: If download fails (e.g., NoSuchKey).
        """
        try:
            self._client.download_fileobj(self._bucket, key, file_obj)
            _logger.info("Downloaded file from S3: key=%s", key)
        except ClientError as e:
            _logger.error(
                "Failed to download file from S3: key=%s, error=%s", key, e)
            raise

    def delete_object(self, key: str) -> None:
        """Delete an S3 object

        Args:
            key: S3 object key

        Raises:
            ClientError: If delete fails.
        """
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
            _logger.info("Deleted file from S3: key=%s", key)
        except ClientError as e:
            _logger.error(
                "Failed to delete file from S3: key=%s, error=%s", key, e)
            raise

    def head_object(self, key: str) -> dict:
        """Retrieve metadata for an S3 object

        Args:
            key: S3 object key

        Returns:
            Dict with object metadata.

        Raises:
            ClientError: If object does not exist or request fails.
        """
        try:
            response = self._client.head_object(Bucket=self._bucket, Key=key)
            return dict(response)
        except ClientError as e:
            _logger.error(
                "Failed to head object in S3: key=%s, error=%s", key, e)
            raise
