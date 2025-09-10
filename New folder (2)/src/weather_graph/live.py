from __future__ import annotations

import httpx
from typing import Dict, Optional


async def _geocode_city(client: httpx.AsyncClient, city: str) -> Optional[Dict[str, float]]:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = await client.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    top = results[0]
    return {"latitude": top["latitude"], "longitude": top["longitude"], "name": top.get("name", city)}


async def fetch_current_weather(city: str) -> Dict:
    async with httpx.AsyncClient() as client:
        coords = await _geocode_city(client, city)
        if coords is None:
            return {"ok": False, "error": f"City not found: {city}"}
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "current_weather": True,
        }
        resp = await client.get(weather_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_weather") or {}
        return {
            "ok": True,
            "city": coords.get("name", city),
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "current": current,
        }


