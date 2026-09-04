import structlog
from typing import Dict, Any, List
from src.integrations.base import BaseAPIClient
from src.config import settings

logger = structlog.get_logger(__name__)

class WeatherClient(BaseAPIClient):
    """OpenWeatherMap API client."""

    def __init__(self):
        super().__init__(base_url="https://api.openweathermap.org/data/2.5/")
        self.api_key = settings.OPENWEATHER_API_KEY

    async def get_current(self, city: str) -> Dict[str, Any]:
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "uz"
        }
        try:
            data = await self.get("weather", params=params)
            return {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"]
            }
        except Exception as e:
            logger.error("Weather get_current failed", city=city, error=str(e))
            raise

    async def get_forecast(self, city: str, days: int) -> List[Dict[str, Any]]:
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "uz",
            "cnt": days * 8 # rough estimate for 3-hour intervals
        }
        try:
            data = await self.get("forecast", params=params)
            return [
                {
                    "datetime": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"]
                }
                for item in data.get("list", [])
            ]
        except Exception as e:
            logger.error("Weather get_forecast failed", city=city, error=str(e))
            raise

    async def search_city(self, query: str) -> List[Dict[str, Any]]:
        # Using Geocoding API if needed, or simple weather query
        params = {
            "q": query,
            "appid": self.api_key,
            "limit": 5
        }
        try:
            # direct geocoding
            client = BaseAPIClient(base_url="http://api.openweathermap.org/geo/1.0/")
            data = await client.get("direct", params=params)
            return [{"name": item["name"], "country": item["country"]} for item in data]
        except Exception as e:
            logger.error("Weather search_city failed", query=query, error=str(e))
            raise

weather_client = WeatherClient()
