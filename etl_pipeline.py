"""Extract, transform, validate, and load air-quality data."""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
from pydantic import ValidationError

from config import CITIES, CSV_PATH, DATA_DIR, DB_PATH, HOURLY_VARIABLES
from models import AirQualityRecord

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def extract_city_data(city: dict[str, Any], forecast_days: int = 1) -> list[dict[str, Any]]:
    """Fetch hourly air-quality measurements for one city from Open-Meteo."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": ",".join(HOURLY_VARIABLES),
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    records = []
    for index, timestamp in enumerate(times):
        record = {
            "city": city["city"],
            "country": city["country"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "timestamp": timestamp,
        }
        for variable in HOURLY_VARIABLES:
            values = hourly.get(variable, [])
            record[variable] = values[index] if index < len(values) else None
        records.append(record)
    return records


def extract_all(cities: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Extract data for all configured cities; continue if one city fails."""
    all_records: list[dict[str, Any]] = []
    failures = []
    for city in cities or CITIES:
        try:
            city_records = extract_city_data(city)
            all_records.extend(city_records)
            print(f"[OK] {city['city']}: extracted {len(city_records)} hourly records")
        except (requests.RequestException, ValueError, KeyError) as exc:
            failures.append(f"{city['city']}: {exc}")
            print(f"[WARNING] Could not fetch {city['city']}: {exc}")
    if not all_records:
        details = "\n".join(failures) if failures else "The API returned no records."
        raise RuntimeError(
            "No data was downloaded. Check your internet connection and try again.\n" + details
        )
    return all_records


def transform_and_validate(raw_records: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize fields, validate with Pydantic, remove duplicates, and sort."""
    valid_records = []
    rejected = 0
    for item in raw_records:
        try:
            validated = AirQualityRecord.model_validate(item)
            valid_records.append(validated.model_dump())
        except ValidationError as exc:
            rejected += 1
            print(f"[WARNING] Rejected invalid record: {exc.errors()[0]['msg']}")
    if rejected:
        print(f"[INFO] Rejected {rejected} invalid record(s).")

    if not valid_records:
        raise RuntimeError("No valid records remained after validation.")

    df = pd.DataFrame(valid_records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    numeric_columns = [
        "latitude", "longitude", "pm10", "pm2_5", "carbon_monoxide",
        "nitrogen_dioxide", "sulphur_dioxide", "ozone", "us_aqi", "european_aqi"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Keep missing pollutant readings as NaN; do not invent replacement values.
    df = df.dropna(subset=["city", "timestamp"])
    before = len(df)
    df = df.drop_duplicates(subset=["city", "timestamp"], keep="last")
    print(f"[INFO] Removed {before - len(df)} duplicate record(s).")
    df = df.sort_values(["city", "timestamp"]).reset_index(drop=True)
    df["extracted_at_utc"] = datetime.now(timezone.utc).isoformat()
    return df


def load_data(df: pd.DataFrame) -> None:
    """Save processed data to CSV and SQLite."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql("air_quality", connection, if_exists="replace", index=False)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_city_timestamp ON air_quality (city, timestamp)"
        )
    print(f"[OK] CSV saved to: {CSV_PATH}")
    print(f"[OK] SQLite database saved to: {DB_PATH}")


def run_pipeline() -> pd.DataFrame:
    """Run the complete ETL pipeline."""
    print("Starting Air Quality ETL pipeline...")
    raw_records = extract_all()
    print(f"[INFO] Total raw records: {len(raw_records)}")
    clean_df = transform_and_validate(raw_records)
    print(f"[INFO] Valid processed records: {len(clean_df)}")
    load_data(clean_df)
    print("ETL pipeline completed successfully.")
    return clean_df


if __name__ == "__main__":
    try:
        result = run_pipeline()
        print("\nPreview:")
        print(result.head(10).to_string(index=False))
    except Exception as error:
        print(f"\nPipeline failed: {error}", file=sys.stderr)
        sys.exit(1)
