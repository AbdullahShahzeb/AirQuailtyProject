"""Configuration for the Air Quality ETL + EDA project."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
DB_PATH = DATA_DIR / "air_quality.db"
CSV_PATH = DATA_DIR / "air_quality_data.csv"

# Open-Meteo Air Quality API coordinates. Change these to study other locations.
CITIES = [
    {"city": "Lahore", "country": "Pakistan", "latitude": 31.5204, "longitude": 74.3587},
    {"city": "Karachi", "country": "Pakistan", "latitude": 24.8607, "longitude": 67.0011},
    {"city": "Islamabad", "country": "Pakistan", "latitude": 33.6844, "longitude": 73.0479},
    {"city": "Peshawar", "country": "Pakistan", "latitude": 34.0151, "longitude": 71.5249},
    {"city": "Quetta", "country": "Pakistan", "latitude": 30.1798, "longitude": 66.9750},
]

HOURLY_VARIABLES = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "us_aqi",
    "european_aqi",
]
