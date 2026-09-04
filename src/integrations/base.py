import asyncio
import httpx
import structlog
from typing import Any, Dict, Optional, Callable, TypeVar, Mapping
from httpx import HTTPStatusError, RequestError

logger = structlog.get_logger(__name__)
T = TypeVar("T")

class BaseAPIClient:
    """Base API client with retry mechanism."""

    def __init__(self, base_url: str = "", timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        **kwargs: Any
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        json=json_data,
                        data=data,
                        headers=headers,
                        **kwargs
                    )
                    response.raise_for_status()
                    # Return JSON if possible, otherwise text or bytes
                    if "application/json" in response.headers.get("Content-Type", ""):
                        return response.json()
                    return response.text
            except (HTTPStatusError, RequestError) as e:
                logger.warning(
                    f"API request failed (attempt {attempt + 1}/{self.max_retries})",
                    url=url,
                    error=str(e)
                )
                if attempt == self.max_retries - 1:
                    logger.error("Max retries reached", url=url, error=str(e))
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def get(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._request("POST", endpoint, **kwargs)
