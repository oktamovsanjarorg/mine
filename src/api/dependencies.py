from typing import AsyncGenerator, Annotated
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import async_session_maker
from src.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting DB session."""
    async with async_session_maker() as session:
        yield session

def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Verify admin API key."""
    if not settings.API_KEY or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API Key"
        )
    return api_key

DbSession = Annotated[AsyncSession, Depends(get_db)]
ApiKey = Annotated[str, Depends(verify_api_key)]
