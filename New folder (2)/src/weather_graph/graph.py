from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .heuristics import analyze_with_heuristics
from .types import WeatherResult, WeatherState

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore


def _has_openai_key() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def _llm_analyze(text: str) -> WeatherResult:
    if ChatOpenAI is None:
        raise RuntimeError("LLM backend not available")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    system = (
        "You identify whether a text is a local weather report and extract fields: "
        "location, temperature, condition, and time. Respond JSON with keys: "
        "is_weather_report (bool), confidence (0..1), location, temperature, condition, time, rationale."
    )
    user = f"Text: {text}"
    response = model.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    content: str = response.content if hasattr(response, "content") else str(response)
    # Best-effort: try to parse JSON; fall back to heuristics-like extraction if needed
    try:
        import json

        data = json.loads(content)
        return WeatherResult(**data)
    except Exception:
        # Fallback minimal structure
        heur = analyze_with_heuristics(text)
        heur.rationale = "LLM freeform response; fell back to heuristics for structure."
        return heur


def _classify(state: WeatherState) -> WeatherState:
    text = state.text
    load_dotenv(override=False)
    use_llm = state.use_llm and _has_openai_key()
    if use_llm:
        try:
            result = _llm_analyze(text)
        except Exception:
            result = analyze_with_heuristics(text)
    else:
        result = analyze_with_heuristics(text)
    state.result = result
    state.meta["used_llm"] = bool(use_llm)
    return state


def _is_weather_report(state: WeatherState) -> str:
    return END if state.result.is_weather_report else END


def build_weather_graph() -> Any:
    graph = StateGraph(WeatherState)
    graph.add_node("classify", _classify)
    graph.set_entry_point("classify")
    graph.add_edge("classify", END)
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


