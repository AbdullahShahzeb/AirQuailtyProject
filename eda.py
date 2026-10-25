"""Exploratory data analysis and charts for the air-quality dataset."""
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import DB_PATH, OUTPUT_DIR


def load_from_database() -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run `python etl_pipeline.py` before running EDA."
        )
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query("SELECT * FROM air_quality", connection)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df


def create_eda_outputs(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pollutant_columns = [
        "pm2_5", "pm10", "carbon_monoxide", "nitrogen_dioxide",
        "sulphur_dioxide", "ozone", "us_aqi", "european_aqi"
    ]
    available = [column for column in pollutant_columns if column in df.columns]

    print("\n=== DATASET OVERVIEW ===")
    print(f"Rows: {len(df)}")
    print(f"Cities: {df['city'].nunique()}")
    print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print("\n=== DATA TYPES ===")
    print(df.dtypes.to_string())
    print("\n=== MISSING VALUES ===")
    print(df.isna().sum().to_string())
    print("\n=== DUPLICATE ROWS ===")
    print(int(df.duplicated(subset=["city", "timestamp"]).sum()))
    print("\n=== SUMMARY STATISTICS ===")
    print(df[available].describe().round(2).to_string())

    # Average AQI by city.
    if "us_aqi" in df.columns:
        city_aqi = df.groupby("city", dropna=False)["us_aqi"].mean().dropna().sort_values()
        if not city_aqi.empty:
            ax = city_aqi.plot(kind="bar", figsize=(9, 5), title="Average US AQI by City")
            ax.set_xlabel("City")
            ax.set_ylabel("US AQI (higher generally indicates worse air quality)")
            plt.xticks(rotation=25, ha="right")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "average_aqi_by_city.png", dpi=150)
            plt.close()

    # Mean particulate matter by city.
    particulate = [c for c in ["pm2_5", "pm10"] if c in df.columns]
    if particulate:
        means = df.groupby("city")[particulate].mean()
        ax = means.plot(kind="bar", figsize=(9, 5), title="Average Particulate Matter by City")
        ax.set_xlabel("City")
        ax.set_ylabel("Concentration (unit supplied by API, typically µg/m³)")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "particulate_matter_by_city.png", dpi=150)
        plt.close()

    # PM2.5 over time for each city.
    if "pm2_5" in df.columns and "timestamp" in df.columns:
        pivot = df.pivot_table(index="timestamp", columns="city", values="pm2_5", aggfunc="mean")
        if not pivot.empty:
            ax = pivot.plot(figsize=(10, 5), title="Hourly PM2.5 by City")
            ax.set_xlabel("Time (UTC)")
            ax.set_ylabel("PM2.5 concentration (µg/m³)")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "hourly_pm25_by_city.png", dpi=150)
            plt.close()

    # Export city-level summary for report/dashboard.
    summary_columns = [c for c in ["pm2_5", "pm10", "us_aqi", "european_aqi"] if c in df.columns]
    summary = df.groupby("city")[summary_columns].agg(["mean", "min", "max"]).round(2)
    summary.to_csv(OUTPUT_DIR / "city_summary.csv")
    print(f"\nEDA files saved in: {OUTPUT_DIR}")
    print("Charts: average_aqi_by_city.png, particulate_matter_by_city.png, hourly_pm25_by_city.png")
    print("Summary: city_summary.csv")


if __name__ == "__main__":
    dataset = load_from_database()
    create_eda_outputs(dataset)
