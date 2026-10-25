# Air Quality ETL + Exploratory Data Analysis (EDA)

## Project overview
This project downloads hourly air-quality data for five cities in Pakistan from the Open-Meteo Air Quality API. It validates and transforms records with **Pydantic** and **Pandas**, loads them into **CSV** and **SQLite**, performs EDA, and provides a **Streamlit dashboard**.

### Cities
- Lahore
- Karachi
- Islamabad
- Peshawar
- Quetta

### Variables
- PM2.5 and PM10 particulate matter
- Carbon monoxide (CO)
- Nitrogen dioxide (NO₂)
- Sulphur dioxide (SO₂)
- Ozone (O₃)
- US AQI and European AQI

## Requirements
- Python 3.10 or newer
- Internet connection for API extraction

## Setup
Open a terminal in this project folder.

### 1. Create a virtual environment (recommended)
Windows:
```bash
python -m venv .venv
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the ETL pipeline
```bash
python etl_pipeline.py
```
This extracts API data, validates each record with Pydantic, cleans/sorts it with Pandas, removes duplicate city/timestamp records, then saves:
- `data/air_quality_data.csv`
- `data/air_quality.db` (SQLite table: `air_quality`)

### 4. Run EDA and create charts
```bash
python eda.py
```
Outputs are saved in `outputs/`:
- `city_summary.csv`
- `average_aqi_by_city.png`
- `particulate_matter_by_city.png`
- `hourly_pm25_by_city.png`

Some charts may not be created if the API does not return the required variable for the selected period.

### 5. Run the dashboard
```bash
streamlit run app.py
```
Open the local URL shown in the terminal. Click **Refresh data from API** in the sidebar to fetch fresh data.

## ETL design
1. **Extract:** `requests` calls the Open-Meteo Air Quality API for each configured city.
2. **Transform:** Pandas converts data types, sorts observations, and removes duplicate city/timestamp records. Missing readings remain missing rather than being fabricated.
3. **Validate:** Pydantic checks coordinates, required city fields, timestamp format, and non-negative pollutant/AQI values.
4. **Load:** The cleaned data is stored in a CSV file and an SQLite database.
5. **EDA:** Summary statistics, missing values, duplicate checks, city comparisons, and time trends are produced.

## Project description for submission form
**Problem:** Air pollution affects public health and the environment. Comparing pollutant levels across cities can help people understand patterns in air quality.

**Dataset:** This project uses hourly air-quality data from the Open-Meteo Air Quality API for Lahore, Karachi, Islamabad, Peshawar, and Quetta. Variables include PM2.5, PM10, selected gases, and AQI indicators.

**What we will build:** A Python ETL pipeline that extracts data from the API, transforms it with Pandas, validates records with Pydantic, and loads processed data into CSV and SQLite. EDA will summarize missing values and descriptive statistics, compare average pollutant/AQI values across cities, and visualize hourly trends using Matplotlib. A Streamlit dashboard will display the dataset and charts.

**Expected result:** A repeatable pipeline and interactive dashboard for exploring air-quality data across selected cities.

## Limitations
- The API may return forecast/modelled data rather than readings from official local monitoring stations.
- Internet access is required to refresh data.
- AQI values and pollutant units depend on the API's definitions. Refer to Open-Meteo documentation before interpreting results.
- This is an educational project, not a health-warning or regulatory monitoring system.

## API reference
Open-Meteo Air Quality API: https://air-quality-api.open-meteo.com/v1/air-quality
Documentation: https://open-meteo.com/en/docs/air-quality-api

## Suggested GitHub repository description
Python ETL pipeline and EDA dashboard for hourly air-quality data using Open-Meteo API, Pandas, Pydantic, SQLite, Matplotlib, and Streamlit.
