from __future__ import annotations

import re
from typing import Optional, Tuple

from .types import WeatherResult


WEATHER_KEYWORDS = [
    "rain",
    "snow",
    "sunny",
    "cloudy",
    "overcast",
    "storm",
    "thunder",
    "drizzle",
    "shower",
    "windy",
    "humid",
    "fog",
    "mist",
    "hail",
    "heat",
    "cool",
    "cold",
    "warm",
]


TEMP_PATTERN = re.compile(r"(-?\d{1,3})\s?(?:°\s?)?(?:F|C|fahrenheit|celsius)?", re.IGNORECASE)
LOCATION_PATTERN = re.compile(
    r"(?:in|at|for)\s+([A-Z][A-Za-z\-\s]{2,}(?:,\s*[A-Z]{2})?)",
    re.IGNORECASE,
)
TIME_PATTERN = re.compile(
    r"\b(this\s+morning|this\s+afternoon|tonight|today|tomorrow|\d{1,2}\s?(?:am|pm))\b",
    re.IGNORECASE,
)


def _find_condition(text: str) -> Optional[str]:
    lower = text.lower()
    for word in WEATHER_KEYWORDS:
        if word in lower:
            return word
    return None


def _find_temp(text: str) -> Optional[str]:
    match = TEMP_PATTERN.search(text)
    if not match:
        return None
    value = match.group(1)
    # Best-effort: infer unit if present in text
    unit = "°F" if re.search(r"f(ahrenheit)?", text, re.IGNORECASE) else None
    unit = unit or ("°C" if re.search(r"c(elsius)?", text, re.IGNORECASE) else None)
    return f"{value}{unit or ''}"


def _find_location(text: str) -> Optional[str]:
    match = LOCATION_PATTERN.search(text)
    return match.group(1).strip() if match else None


def _find_time(text: str) -> Optional[str]:
    match = TIME_PATTERN.search(text)
    return match.group(1).strip() if match else None


def analyze_with_heuristics(text: str) -> WeatherResult:
    condition = _find_condition(text)
    temperature = _find_temp(text)
    location = _find_location(text)
    time = _find_time(text)

    signals = 0
    if condition:
        signals += 1
    if temperature:
        signals += 1
    if location:
        signals += 1

    is_weather = signals >= 2 or (condition is not None and "weather" in text.lower())
    confidence = min(1.0, 0.4 + 0.2 * signals)

    return WeatherResult(
        is_weather_report=is_weather,
        confidence=confidence,
        location=location,
        temperature=temperature,
        condition=condition,
        time=time,
        rationale="Heuristic classification based on keywords, temperature, and location cues.",
    )


