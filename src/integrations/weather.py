import structlog
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from src.integrations.base import BaseAPIClient
from src.config import settings

logger = structlog.get_logger(__name__)


class WeatherClient(BaseAPIClient):
    """Weather client supporting OpenWeatherMap and free Open-Meteo fallback."""

    def __init__(self):
        super().__init__(base_url="https://api.openweathermap.org/data/2.5/")

    @property
    def api_key(self) -> Optional[str]:
        raw = settings.openweather_api_key or settings.weather_api_key
        if raw and hasattr(raw, "get_secret_value"):
            return raw.get_secret_value()
        return str(raw) if raw else None

    async def get_current(self, city: str = "Tashkent") -> Dict[str, Any]:
        """Get current weather for city."""
        key = self.api_key
        if key:
            params = {
                "q": city,
                "appid": key,
                "units": "metric",
                "lang": "uz"
            }
            try:
                data = await self.get("weather", params=params)
                return {
                    "city": city,
                    "temp": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "wind": data["wind"]["speed"],
                }
            except Exception as e:
                logger.warning("OpenWeatherMap failed, using fallback", error=str(e))

        # Fallback to free Open-Meteo for Tashkent (no API key needed)
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.open-meteo.com/v1/forecast?latitude=41.2995&longitude=69.2401&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Asia%2FTashkent"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        current = data.get("current", {})
                        temp = current.get("temperature_2m", 25.0)
                        return {
                            "city": "Toshkent",
                            "temp": round(temp, 1),
                            "feels_like": round(temp, 1),
                            "humidity": current.get("relative_humidity_2m", 40),
                            "description": "Ochiq havo",
                            "wind": current.get("wind_speed_10m", 3.0),
                        }
        except Exception as e:
            logger.error("Open-Meteo current weather fallback failed", error=str(e))

        return {
            "city": "Toshkent",
            "temp": 25.0,
            "feels_like": 25.0,
            "humidity": 40,
            "description": "Ochiq",
            "wind": 2.0,
        }

    async def check_temperature_difference(self, city: str = "Tashkent", threshold: float = 10.0) -> Tuple[bool, str]:
        """
        Check if tomorrow's temperature sharply differs from today's by >= threshold (default 10°C).
        Rule: ONLY return True if difference >= 10°C. If difference < 10°C, return False (no spam).
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.open-meteo.com/v1/forecast?latitude=41.2995&longitude=69.2401&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTashkent"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        daily = data.get("daily", {})
                        max_temps = daily.get("temperature_2m_max", [])
                        min_temps = daily.get("temperature_2m_min", [])
                        
                        if len(max_temps) >= 2 and len(min_temps) >= 2:
                            today_avg = (max_temps[0] + min_temps[0]) / 2.0
                            tomorrow_avg = (max_temps[1] + min_temps[1]) / 2.0
                            diff = tomorrow_avg - today_avg
                            abs_diff = abs(diff)

                            # ONLY alert if difference is >= threshold (10°C)
                            if abs_diff >= threshold:
                                change_word = "isinish" if diff > 0 else "sovish"
                                direction_emoji = "📈" if diff > 0 else "📉"
                                msg = (
                                    f"⚠️ <b>DIQQAT: Ob-havoda keskin o'zgarish!</b>\n\n"
                                    f"Bugungi o'rtacha harorat: <b>{today_avg:.1f}°C</b>\n"
                                    f"Ertangi o'rtacha harorat: <b>{tomorrow_avg:.1f}°C</b>\n\n"
                                    f"{direction_emoji} <b>Kutilayotgan farq: {abs_diff:.1f}°C ({change_word})!</b>\n"
                                    f"Iltimos, kiyinishingiz va rejalaringizda ehtiyot bo'ling!"
                                )
                                return True, msg
        except Exception as e:
            logger.error("Failed to check temperature difference", error=str(e))

        # Difference is less than 10 degrees or couldn't check -> do NOT alert!
        return False, ""


weather_client = WeatherClient()
