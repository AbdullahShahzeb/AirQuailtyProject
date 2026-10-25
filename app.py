"""Streamlit dashboard for the Air Quality ETL + EDA project."""
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from config import DB_PATH
from etl_pipeline import run_pipeline

st.set_page_config(page_title="Air Quality Explorer", page_icon="🌫️", layout="wide")
st.title("🌫️ Air Quality ETL + EDA Dashboard")
st.write(
    "Collects hourly air-quality measurements from the Open-Meteo API, validates them, "
    "stores them in SQLite/CSV, and summarizes pollutant patterns."
)

with st.sidebar:
    st.header("Controls")
    if st.button("Refresh data from API", type="primary"):
        with st.spinner("Downloading, validating, and saving data..."):
            try:
                run_pipeline()
                st.success("Data refreshed successfully.")
            except Exception as exc:
                st.error(f"Refresh failed: {exc}")

if not DB_PATH.exists():
    st.info("No local dataset found yet. Click **Refresh data from API** in the sidebar.")
    st.stop()

with sqlite3.connect(DB_PATH) as connection:
    df = pd.read_sql_query("SELECT * FROM air_quality", connection)

if df.empty:
    st.warning("The database has no records. Refresh the data to continue.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
cities = sorted(df["city"].dropna().unique().tolist())
selected_cities = st.multiselect("Choose cities", cities, default=cities)
filtered = df[df["city"].isin(selected_cities)].copy()

if filtered.empty:
    st.warning("Choose at least one city.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Records", f"{len(filtered):,}")
c2.metric("Cities selected", f"{filtered['city'].nunique()}")
c3.metric("Latest measurement (UTC)", str(filtered["timestamp"].max())[:16])

st.subheader("Dataset preview")
st.dataframe(filtered.head(100), use_container_width=True)

st.subheader("Summary statistics")
metrics = [c for c in ["pm2_5", "pm10", "us_aqi", "european_aqi"] if c in filtered.columns]
if metrics:
    st.dataframe(filtered.groupby("city")[metrics].agg(["mean", "min", "max"]).round(2),
                 use_container_width=True)

left, right = st.columns(2)
with left:
    if "us_aqi" in filtered.columns:
        avg_aqi = filtered.groupby("city")["us_aqi"].mean().dropna().sort_values(ascending=False)
        if not avg_aqi.empty:
            fig, ax = plt.subplots(figsize=(7, 4))
            avg_aqi.plot(kind="bar", ax=ax)
            ax.set_title("Average US AQI by City")
            ax.set_ylabel("US AQI")
            ax.set_xlabel("City")
            plt.xticks(rotation=25, ha="right")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
with right:
    particles = [c for c in ["pm2_5", "pm10"] if c in filtered.columns]
    if particles:
        means = filtered.groupby("city")[particles].mean()
        fig, ax = plt.subplots(figsize=(7, 4))
        means.plot(kind="bar", ax=ax)
        ax.set_title("Average Particulate Matter by City")
        ax.set_ylabel("Concentration (typically µg/m³)")
        ax.set_xlabel("City")
        plt.xticks(rotation=25, ha="right")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

if "pm2_5" in filtered.columns:
    st.subheader("Hourly PM2.5 trend")
    trend = filtered.pivot_table(index="timestamp", columns="city", values="pm2_5", aggfunc="mean")
    st.line_chart(trend)

st.subheader("Data quality checks")
quality1, quality2 = st.columns(2)
quality1.metric("Missing cells", int(filtered.isna().sum().sum()))
quality2.metric("Duplicate city/time records",
                int(filtered.duplicated(subset=["city", "timestamp"]).sum()))

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="air_quality_data.csv",
    mime="text/csv",
)
st.caption(
    "Data is retrieved from Open-Meteo. Measurements are API estimates/forecasts for the selected "
    "coordinates and should not be treated as official regulatory monitoring readings."
)
