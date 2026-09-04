import structlog
import json
import csv
from io import StringIO
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.export import ExportRepository

logger = structlog.get_logger(__name__)

class ExportService:
    """Service for data exports."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ExportRepository(session)

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Gather all user data for export."""
        return await self.repo.get_all_user_data(user_id)

    async def export_to_json(self, user_id: int) -> str:
        """Export module data to JSON."""
        data = await self.get_user_data(user_id)
        return json.dumps(data, default=str, ensure_ascii=False, indent=2)

    async def export_to_csv(self, user_id: int, module: str) -> str:
        """Export specific module data to CSV."""
        data = await self.repo.get_module_data(user_id, module)
        if not data:
            return ""
            
        output = StringIO()
        if isinstance(data, list) and len(data) > 0:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return output.getvalue()

    async def export_to_html(self, user_id: int) -> str:
        """Export module data to HTML."""
        data = await self.get_user_data(user_id)
        # Simplified HTML generator
        html = f"<html><head><title>Eksport - {user_id}</title></head><body><h1>Sizning ma'lumotlaringiz</h1>"
        html += f"<pre>{json.dumps(data, default=str, indent=2)}</pre>"
        html += "</body></html>"
        return html

    async def export_to_pdf(self, user_id: int) -> bytes:
        """Export module data to PDF."""
        # Mocking PDF generation
        return b"%PDF-1.4\n%Mock PDF document for user data\n%%EOF"
