# Flight Finder

Two-page JavaScript UI with a Python/FastAPI live-flight backend and a small ML delay-risk model. Live Google results are retrieved through SerpApi.

## Run

In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SERPAPI_API_KEY = "your_serpapi_key"
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`. The supplied `IB5634` result is bundled as [data/ib5634_serpapi.json](data/ib5634_serpapi.json) and can be viewed without a key by choosing date `2026-04-23`. For any live search, set `SERPAPI_API_KEY`.

The displayed delay percentage is a model estimate trained on generated demo data—replace it with licensed historical on-time data before making operational decisions.
