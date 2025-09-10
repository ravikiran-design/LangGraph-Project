from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WeatherResult(BaseModel):
    is_weather_report: bool = Field(default=False)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    location: Optional[str] = None
    temperature: Optional[str] = None
    condition: Optional[str] = None
    time: Optional[str] = None
    rationale: Optional[str] = None


class WeatherState(BaseModel):
    text: str
    use_llm: bool = Field(default=False)
    result: WeatherResult = Field(default_factory=WeatherResult)
    meta: Dict[str, Any] = Field(default_factory=dict)

