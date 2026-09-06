"""Flight Finder: FastAPI backend + a small delay-risk ML model.

Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET before starting the app.
Create free test credentials at https://developers.amadeus.com/.
"""
import asyncio
import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from sklearn.ensemble import RandomForestClassifier


app = FastAPI(title="Flight Finder")
app.mount("/static", StaticFiles(directory="static"), name="static")
SAMPLE_DATA_FILE = Path("data/ib5634_serpapi.json")


def build_delay_model() -> RandomForestClassifier:
    """Train a tiny deterministic demo classifier at startup.

    Replace this generated sample with historical airline/on-time data when
    deploying. Inputs are departure hour, route length, weekend, and carrier.
    """
    rng = np.random.default_rng(42)
    n = 2500
    hour = rng.integers(0, 24, n)
    distance = rng.integers(250, 9000, n)
    weekend = rng.integers(0, 2, n)
    carrier_code = rng.integers(0, 8, n)
    # Late-day, longer flights and a small carrier effect raise delay chance.
    score = -3.0 + 0.09 * np.maximum(hour - 14, 0) + distance / 9000
    score += 0.22 * weekend + 0.12 * carrier_code + rng.normal(0, 0.6, n)
    delayed = (score > 0).astype(int)
    model = RandomForestClassifier(n_estimators=100, min_samples_leaf=8, random_state=42)
    model.fit(np.column_stack((hour, distance, weekend, carrier_code)), delayed)
    return model


delay_model = build_delay_model()


class FlightSearch(BaseModel):
    flight_number: str
    departure_date: date

    @field_validator("flight_number")
    @classmethod
    def validate_flight_number(cls, value: str) -> str:
        cleaned = re.sub(r"\s+", "", value.upper())
        if not re.fullmatch(r"[A-Z0-9]{2,3}\d{1,4}[A-Z]?", cleaned):
            raise ValueError("Use a number like AI101, 6E234 or BA256")
        return cleaned


def credentials_present() -> bool:
    return bool(os.getenv("AMADEUS_CLIENT_ID") and os.getenv("AMADEUS_CLIENT_SECRET"))


def serpapi_credentials_present() -> bool:
    return bool(os.getenv("SERPAPI_API_KEY"))


async def amadeus_token(client: httpx.AsyncClient) -> str:
    response = await client.post(
        f"{os.getenv('AMADEUS_BASE_URL', 'https://test.api.amadeus.com')}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["AMADEUS_CLIENT_ID"],
            "client_secret": os.environ["AMADEUS_CLIENT_SECRET"],
        },
        timeout=15,
    )
    if response.is_error:
        raise HTTPException(502, "Could not authenticate with the flight-data provider.")
    return response.json()["access_token"]


def first_value(obj: Any, *keys: str, default: str = "Not available") -> str:
    if not isinstance(obj, dict):
        return default
    for key in keys:
        if obj.get(key) not in (None, ""):
            return str(obj[key])
    return default


def parse_live_flight(item: dict[str, Any], search: FlightSearch) -> dict[str, Any]:
    segment = (item.get("segments") or [{}])[0]
    departure = segment.get("departure") or item.get("departure") or {}
    arrival = segment.get("arrival") or item.get("arrival") or {}
    aircraft = segment.get("aircraft") or {}
    airline = item.get("operating") or item.get("carrierCode") or search.flight_number[:2]
    scheduled = first_value(departure, "at", "scheduledAt", default=f"{search.departure_date}T12:00:00")
    try:
        departure_hour = datetime.fromisoformat(scheduled.replace("Z", "+00:00")).hour
    except ValueError:
        departure_hour = 12
    # Provider schedules do not always include route distance; use a neutral 1,500 km estimate.
    carrier_number = sum(ord(c) for c in str(airline)) % 8
    risk = float(delay_model.predict_proba([[departure_hour, 1500, int(search.departure_date.weekday() >= 5), carrier_number]])[0][1])
    flight = item.get("flightNumber") or segment.get("number") or re.sub(r"^[A-Z0-9]{2,3}", "", search.flight_number)
    return {
        "flight": f"{item.get('carrierCode', search.flight_number[:2])}{flight}",
        "airline": str(airline),
        "status": first_value(item, "status", default="Scheduled"),
        "departure": {"airport": first_value(departure, "iataCode", "airportCode", "terminal"), "time": scheduled, "terminal": first_value(departure, "terminal")},
        "arrival": {"airport": first_value(arrival, "iataCode", "airportCode", "terminal"), "time": first_value(arrival, "at", "scheduledAt"), "terminal": first_value(arrival, "terminal")},
        "aircraft": first_value(aircraft, "code", "name"),
        "delay_risk_percent": round(risk * 100),
        "data_note": "Live schedule data supplied by Amadeus; delay risk is an ML estimate, not a live status.",
    }


def parse_serpapi_flight(flight_result: dict[str, Any], search: FlightSearch) -> dict[str, Any]:
    """Convert SerpApi's Google `flight_result` into the UI's stable format."""
    available = flight_result.get("dates", [])
    chosen = next((x for x in available if x.get("date") == search.departure_date.isoformat()), None)
    chosen = chosen or next((x for x in available if x.get("departure_airport")), None)
    if not chosen:
        raise HTTPException(404, "Google returned no detailed schedule for that flight/date.")
    meta = chosen.get("metadata", {})
    departure, arrival = chosen.get("departure_airport", {}), chosen.get("arrival_airport", {})
    time_text = departure.get("scheduled_time") or departure.get("time") or f"{search.departure_date}T12:00:00"
    try:
        hour = datetime.fromisoformat(time_text.replace("Z", "+00:00")).hour
    except ValueError:
        hour = 12
    airline_code = meta.get("airline_iata_code", flight_result.get("airline_iata_code", ""))
    carrier_number = sum(ord(c) for c in airline_code) % 8
    risk = float(delay_model.predict_proba([[hour, 1500, int(search.departure_date.weekday() >= 5), carrier_number]])[0][1])
    return {
        "flight": chosen.get("flight_designator", flight_result.get("flight_designator", search.flight_number)),
        "airline": flight_result.get("airline", airline_code or "Not available"),
        "status": chosen.get("status", meta.get("status", "Scheduled")).replace("_", " ").title(),
        "departure": {"airport": departure.get("id", meta.get("origin", "Not available")), "time": time_text, "terminal": departure.get("terminal", "Not available")},
        "arrival": {"airport": arrival.get("id", meta.get("destination", "Not available")), "time": arrival.get("scheduled_time", arrival.get("time", "Not available")), "terminal": arrival.get("terminal", "Not available")},
        "aircraft": "Not available from Google flight result",
        "delay_risk_percent": round(risk * 100),
        "data_note": f"Google flight result via SerpApi. Source: {chosen.get('source', 'Google')}. ML delay risk is an estimate.",
    }


def sample_flight_result() -> dict[str, Any]:
    with SAMPLE_DATA_FILE.open(encoding="utf-8") as source:
        return json.load(source)["flight_result"]


async def get_serpapi_result(search: FlightSearch) -> dict[str, Any]:
    """Execute the SerpApi code path requested by the user without exposing its key."""
    if not serpapi_credentials_present():
        if search.flight_number == "IB5634":
            return sample_flight_result()
        raise HTTPException(503, "Set SERPAPI_API_KEY for live Google flight searches. IB5634 works with the included sample JSON.")
    try:
        import serpapi
        client = serpapi.Client(api_key=os.environ["SERPAPI_API_KEY"])
        results = await asyncio.to_thread(client.search, {
            "engine": "google", "q": f"Flight {search.flight_number}",
            "location": "Austin, Texas, United States", "google_domain": "google.com",
            "hl": "en", "gl": "us",
        })
        return results["flight_result"]
    except KeyError as error:
        raise HTTPException(404, "Google returned no flight card for this search.") from error
    except Exception as error:
        raise HTTPException(502, f"SerpApi search failed: {error}") from error


@app.get("/")
async def search_page():
    return FileResponse("static/index.html")


@app.get("/results")
async def results_page():
    return FileResponse("static/results.html")


@app.post("/api/flight")
async def get_flight(search: FlightSearch):
    # SerpApi/Google is the primary provider. It also enables the included IB5634
    # JSON demo without credentials.
    if serpapi_credentials_present() or search.flight_number == "IB5634":
        return parse_serpapi_flight(await get_serpapi_result(search), search)
    if not credentials_present():
        raise HTTPException(503, "Set SERPAPI_API_KEY to enable live Google flight search.")
    match = re.fullmatch(r"([A-Z0-9]{2,3})(\d{1,4}[A-Z]?)", search.flight_number)
    assert match
    carrier, number = match.groups()
    base_url = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")
    async with httpx.AsyncClient() as client:
        token = await amadeus_token(client)
        response = await client.get(
            f"{base_url}/v2/schedule/flights",
            params={"carrierCode": carrier, "flightNumber": number, "scheduledDepartureDate": search.departure_date.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
    if response.status_code == 404 or not response.json().get("data"):
        raise HTTPException(404, "No flight was found for that number and date.")
    if response.is_error:
        raise HTTPException(502, "The flight-data provider could not return a result.")
    return parse_live_flight(response.json()["data"][0], search)
