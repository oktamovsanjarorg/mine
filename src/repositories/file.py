from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.file import FileRecord

class FileRepository(BaseRepository[FileRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FileRecord)

    async def get_by_type(self, user_id: int, file_type: str, offset: int = 0, limit: int = 10) -> Sequence[FileRecord]:
        stmt = select(FileRecord).where(
            FileRecord.user_id == user_id,
            FileRecord.file_type == file_type,
            FileRecord.is_deleted == False
        ).order_by(FileRecord.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_checksum(self, user_id: int, checksum: str) -> FileRecord | None:
        stmt = select(FileRecord).where(
            FileRecord.user_id == user_id,
            FileRecord.checksum == checksum,
            FileRecord.is_deleted == False
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_storage_stats(self, user_id: int) -> dict:
        total_stmt = select(func.count(FileRecord.id), func.sum(FileRecord.size)).where(
            FileRecord.user_id == user_id,
            FileRecord.is_deleted == False
        )
        total_result = await self.session.execute(total_stmt)
        total_files, total_size = total_result.first() or (0, 0)
        
        type_stmt = select(FileRecord.file_type, func.sum(FileRecord.size)).where(
            FileRecord.user_id == user_id,
            FileRecord.is_deleted == False
        ).group_by(FileRecord.file_type)
        type_result = await self.session.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        return {
            "total_files": total_files or 0,
            "total_size": total_size or 0,
            "by_type": by_type
        }
