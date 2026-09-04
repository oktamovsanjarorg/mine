import structlog
import json
from typing import Dict, Optional
from src.integrations.base import BaseAPIClient
from src.config import settings

# Since we don't have direct access to redis instance here easily, we'll assume a global or mock cache.
# In a real setup we might inject the redis client.
try:
    from src.db.redis import get_redis
except ImportError:
    get_redis = None

logger = structlog.get_logger(__name__)

class CurrencyClient(BaseAPIClient):
    """Exchange rate API client."""

    def __init__(self):
        super().__init__(base_url="https://api.exchangerate-api.com/v4/latest/") # Free tier placeholder

    async def get_rates(self, base: str) -> Dict[str, float]:
        redis_key = f"rates:{base}"
        
        redis = None
        if get_redis:
            redis = await get_redis()
            cached = await redis.get(redis_key)
            if cached:
                return json.loads(cached)

        try:
            data = await self.get(base)
            rates = data.get("rates", {})
            if redis:
                await redis.setex(redis_key, 3600, json.dumps(rates)) # Cache for 1 hour
            return rates
        except Exception as e:
            logger.error("Currency get_rates failed", base=base, error=str(e))
            raise

    async def convert(self, amount: float, from_curr: str, to_curr: str) -> float:
        try:
            rates = await self.get_rates(from_curr)
            if to_curr not in rates:
                raise ValueError(f"Currency {to_curr} not found")
            return amount * rates[to_curr]
        except Exception as e:
            logger.error("Currency convert failed", error=str(e))
            raise

currency_client = CurrencyClient()
