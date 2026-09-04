import structlog
import os
import shutil
import zipfile
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

class BackupService:
    """Service for database and file backups."""
    def __init__(self, session: AsyncSession):
        self.session = session
        # Mock database backup logic
        self.db_path = "/tmp/app.db"
        self.files_dir = "/tmp/files"
        self.backup_dir = "/tmp/backups"

    async def perform_full_backup(self) -> str:
        """Full database + file ZIP backup."""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}.zip")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add DB
                if os.path.exists(self.db_path):
                    zipf.write(self.db_path, "database.db")
                
                # Add files
                if os.path.exists(self.files_dir):
                    for root, _, files in os.walk(self.files_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join("files", os.path.relpath(file_path, self.files_dir))
                            zipf.write(file_path, arcname)
                            
            logger.info("Zaxira nusxasi yaratildi", backup_path=backup_path)
            return backup_path
        except Exception as e:
            logger.error("Zaxira nusxasi yaratishda xatolik", error=str(e))
            raise

    async def restore_from_backup(self, backup_path: str) -> bool:
        """Restore from full database + file ZIP backup."""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError("Zaxira nusxasi topilmadi")
                
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall("/tmp/restore_temp")
                
            # Move extracted files to their places
            if os.path.exists("/tmp/restore_temp/database.db"):
                shutil.move("/tmp/restore_temp/database.db", self.db_path)
            
            if os.path.exists("/tmp/restore_temp/files"):
                shutil.copytree("/tmp/restore_temp/files", self.files_dir, dirs_exist_ok=True)
                
            shutil.rmtree("/tmp/restore_temp")
            logger.info("Zaxira nusxasidan tiklandi", backup_path=backup_path)
            return True
        except Exception as e:
            logger.error("Tiklashda xatolik", error=str(e))
            raise
