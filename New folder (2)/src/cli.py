from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
import asyncio

from src.weather_graph import WeatherState, build_weather_graph
from src.weather_graph.live import fetch_current_weather


app = typer.Typer(add_completion=False)
console = Console()


def _print_result(result_dict: dict) -> None:
    table = Table(title="Weather Report Analysis")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    for key in [
        "is_weather_report",
        "confidence",
        "location",
        "temperature",
        "condition",
        "time",
        "rationale",
    ]:
        table.add_row(key, str(result_dict.get(key)))
    console.print(table)


@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, help="Text to analyze"),
    file: Optional[Path] = typer.Option(None, exists=True, help="Path to a text file"),
    json_only: bool = typer.Option(False, "--json", help="Print JSON only"),
    use_llm: bool = typer.Option(False, help="Enable LLM if key is set"),
):
    """Analyze text or file and identify local weather report details."""
    if not text and not file:
        raise typer.BadParameter("Provide --text or --file")
    content = text or file.read_text(encoding="utf-8")  # type: ignore[arg-type]

    graph = build_weather_graph()
    state = WeatherState(text=content, use_llm=use_llm)
    output = graph.invoke(state, config={"configurable": {"thread_id": "cli"}})
    if hasattr(output, "result"):
        result = output.result.model_dump()
    else:
        res = output.get("result") if isinstance(output, dict) else None
        if hasattr(res, "model_dump"):
            result = res.model_dump()
        elif isinstance(res, dict):
            result = res
        else:
            result = {"is_weather_report": False, "confidence": 0.0}

    if json_only:
        console.print_json(data=result)
    else:
        _print_result(result)


@app.command()
def current(
    city: str = typer.Option(..., help="City name, e.g., Bangalore"),
    json_only: bool = typer.Option(False, "--json", help="Print JSON only"),
):
    """Fetch current weather using Open-Meteo."""
    result = asyncio.run(fetch_current_weather(city))
    if json_only:
        console.print_json(data=result)
    else:
        if not result.get("ok"):
            console.print(f"[red]{result.get('error')}[/red]")
            raise typer.Exit(code=1)
        current = result.get("current", {})
        table = Table(title=f"Current Weather — {result.get('city')}")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")
        for key in ["temperature", "windspeed", "winddirection", "weathercode", "time"]:
            table.add_row(key, str(current.get(key)))
        console.print(table)


if __name__ == "__main__":
    app()


