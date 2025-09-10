## LangGraph Weather Report Identifier

Identify local weather reports in text using a LangGraph workflow with LLM-backed classification/extraction and robust heuristic fallback.

### Features
- Detects whether input text is a local weather report
- Extracts structured fields: location, temperature, condition, and time (if present)
- Works offline with heuristics; improves with an OpenAI API key
- Simple CLI for analyzing text or files

### Requirements
- Python 3.10+

### Setup
```bash
python -m venv .venv
".venv/Scripts/activate"  # Windows PowerShell
pip install -r requirements.txt
```

Optional (LLM features):
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=...
```

### Usage
Analyze text directly:
```bash
python -m src.cli analyze --text "It's 72°F and sunny in Austin this afternoon"
```

Analyze a file:
```bash
python -m src.cli analyze --file samples/input1.txt
```

Output as JSON only:
```bash
python -m src.cli analyze --text "Rain likely in Seattle tonight" --json
```

### Web UI
Start the server:
```bash
uvicorn src.web.app:app --reload
```
Open `http://127.0.0.1:8000/` and enter a location.

### Project Structure
```
src/
  weather_graph/
    __init__.py
    graph.py
    heuristics.py
    types.py
  cli.py
samples/
  input1.txt
  input2.txt
```

### Notes
- Without an API key, the graph uses heuristics and still works.
- With an API key, classification and extraction are enhanced by an LLM.

