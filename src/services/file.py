import structlog
import hashlib
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.file import FileRepository
from src.models.file import FileRecord

logger = structlog.get_logger(__name__)

class MinIOClientMock:
    async def upload(self, path: str, content: bytes) -> str:
        return f"https://minio.local/{path}"
    async def download(self, path: str) -> bytes:
        return b"file content"
    async def delete(self, path: str) -> bool:
        return True

class FileService:
    """Service for managing files."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FileRepository(session)
        self.storage = MinIOClientMock()

    async def upload_file(self, user_id: int, filename: str, content: bytes, content_type: str) -> FileRecord:
        """Upload file with MinIO storage and checksum check."""
        try:
            checksum = hashlib.sha256(content).hexdigest()
            existing = await self.repo.get_by_checksum(checksum)
            
            if existing:
                return existing
                
            path = f"{user_id}/{filename}"
            url = await self.storage.upload(path, content)
            
            file_record = await self.repo.create(
                user_id=user_id,
                filename=filename,
                path=path,
                url=url,
                size=len(content),
                content_type=content_type,
                checksum=checksum
            )
            await self.session.commit()
            return file_record
        except Exception as e:
            await self.session.rollback()
            logger.error("Fayl yuklashda xatolik", error=str(e))
            raise

    async def download_file(self, file_id: int) -> bytes:
        """Download file content."""
        file_record = await self.repo.get_by_id(file_id)
        if not file_record:
            raise ValueError("Fayl topilmadi")
        return await self.storage.download(file_record.path)

    async def delete_file(self, file_id: int) -> bool:
        """Delete a file."""
        file_record = await self.repo.get_by_id(file_id)
        if not file_record:
            return False
            
        await self.storage.delete(file_record.path)
        result = await self.repo.delete(file_id)
        await self.session.commit()
        return result

    async def checksum_duplicate_check(self, content: bytes) -> Optional[FileRecord]:
        """Check if file already exists."""
        checksum = hashlib.sha256(content).hexdigest()
        return await self.repo.get_by_checksum(checksum)

    async def storage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get storage statistics for user."""
        return await self.repo.get_storage_stats(user_id)
