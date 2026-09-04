import io
import structlog
from typing import Optional, List
from miniopy_async import Minio
from miniopy_async.error import S3Error
from datetime import timedelta

from src.config import settings
from src.core.exceptions import StorageError

logger = structlog.get_logger()

client: Optional[Minio] = None

async def init_storage() -> None:
    """Initialize MinIO client and ensure bucket exists."""
    global client
    secret_key = (
        settings.minio_secret_key.get_secret_value()
        if hasattr(settings.minio_secret_key, "get_secret_value")
        else str(settings.minio_secret_key)
    )
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=secret_key,
        secure=settings.minio_secure
    )
    try:
        found = await client.bucket_exists(settings.minio_bucket)
        if not found:
            await client.make_bucket(settings.minio_bucket)
            logger.info("Created MinIO bucket", bucket=settings.minio_bucket)
        else:
            logger.info("MinIO bucket already exists", bucket=settings.minio_bucket)
    except S3Error as err:
        logger.error("Failed to initialize storage", error=str(err))
        raise StorageError(f"Storage initialization failed: {err}")

async def close_storage() -> None:
    """Close MinIO client connections (clears reference)."""
    global client
    if client:
        client = None
        logger.info("Storage connection closed")

async def upload_file(file_data: bytes, path: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file to the storage bucket."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        data_stream = io.BytesIO(file_data)
        data_size = len(file_data)
        await client.put_object(
            settings.minio_bucket,
            path,
            data_stream,
            data_size,
            content_type=content_type
        )
        return path
    except S3Error as e:
        logger.error("Upload failed", path=path, error=str(e))
        raise StorageError(f"Failed to upload file {path}: {e}")

async def download_file(path: str) -> bytes:
    """Download a file from the storage bucket."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        response = await client.get_object(settings.minio_bucket, path)
        data = await response.read()
        return data
    except S3Error as e:
        logger.error("Download failed", path=path, error=str(e))
        raise StorageError(f"Failed to download file {path}: {e}")
    finally:
        if 'response' in locals():
            response.close()
            response.release_conn()

async def delete_file(path: str) -> None:
    """Delete a file from the storage bucket."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        await client.remove_object(settings.minio_bucket, path)
    except S3Error as e:
        logger.error("Delete failed", path=path, error=str(e))
        raise StorageError(f"Failed to delete file {path}: {e}")

async def get_presigned_url(path: str, expires: int = 3600) -> str:
    """Generate a presigned URL to access a file."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        url = await client.presigned_get_object(
            settings.minio_bucket,
            path,
            expires=timedelta(seconds=expires)
        )
        return url
    except S3Error as e:
        logger.error("Presigned URL generation failed", path=path, error=str(e))
        raise StorageError(f"Failed to generate url for {path}: {e}")

async def get_file_size(path: str) -> int:
    """Get the size of a file in the storage bucket."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        stat = await client.stat_object(settings.minio_bucket, path)
        return stat.size
    except S3Error as e:
        logger.error("Stat failed", path=path, error=str(e))
        raise StorageError(f"Failed to get size for {path}: {e}")

async def list_files(prefix: str) -> List[str]:
    """List all files in the storage bucket under a specific prefix."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        objects = await client.list_objects(settings.minio_bucket, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        logger.error("List files failed", prefix=prefix, error=str(e))
        raise StorageError(f"Failed to list files with prefix {prefix}: {e}")

async def file_exists(path: str) -> bool:
    """Check if a file exists in the storage bucket."""
    if not client:
        raise StorageError("Storage not initialized")
    try:
        await client.stat_object(settings.minio_bucket, path)
        return True
    except S3Error:
        return False
