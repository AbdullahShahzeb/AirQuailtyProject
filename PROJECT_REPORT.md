# University Project Report
## Air Quality ETL and Exploratory Data Analysis Pipeline

### 1. Introduction
Air pollution is an important environmental issue. Air-quality data can contain several measurements, including PM2.5, PM10, and gases such as ozone and nitrogen dioxide. This project collects air-quality information for selected Pakistani cities and analyzes it through a repeatable Python pipeline.

### 2. Problem statement
Raw data from online APIs is not always ready for analysis. Data may contain missing readings, inconsistent data types, or duplicate records. The project addresses this problem by extracting data from an API, validating and cleaning it, storing it in structured formats, and performing exploratory analysis.

### 3. Objectives
- Collect hourly air-quality data for five cities.
- Validate records using Pydantic.
- Clean and transform the data using Pandas.
- Store the processed data in CSV and SQLite.
- Analyze descriptive statistics, missing values, and duplicate records.
- Compare pollutant/AQI values between cities.
- Display findings through charts and a Streamlit dashboard.

### 4. Dataset and source
The dataset is retrieved from the Open-Meteo Air Quality API. The configured locations are Lahore, Karachi, Islamabad, Peshawar, and Quetta. The requested fields are PM2.5, PM10, carbon monoxide, nitrogen dioxide, sulphur dioxide, ozone, US AQI, and European AQI, along with city coordinates and timestamps.

### 5. Tools and technologies
- Python: main programming language.
- Requests: sends HTTP requests to the API.
- Pandas: data transformation and analysis.
- Pydantic: schema and value validation.
- SQLite: relational database storage.
- CSV: portable file storage.
- Matplotlib: charts.
- Streamlit: interactive web dashboard.

### 6. Methodology
**Extract:** The program sends a request to the Open-Meteo API for each configured city and collects hourly observations.

**Transform:** Data is converted into a tabular structure. Numeric columns are converted to numeric types, timestamps are parsed, and records are sorted by city and time.

**Validate:** Pydantic checks that city/country names are present, coordinates are in valid ranges, timestamps can be parsed, and non-null pollutant/AQI readings are non-negative.

**Load:** The final dataset is written to a CSV file and an SQLite database table named `air_quality`.

**EDA:** The analysis calculates summary statistics, checks missing and duplicate records, compares average AQI and particulate matter by city, and visualizes hourly PM2.5 patterns.

### 7. Expected outputs
- Processed CSV dataset.
- SQLite database.
- City-level summary CSV.
- Average AQI by city chart.
- Particulate matter comparison chart.
- Hourly PM2.5 trend chart.
- Streamlit dashboard with filters and CSV download.

### 8. Conclusion
The project demonstrates a complete ETL and EDA workflow. It combines API extraction, data cleaning, schema validation, structured storage, statistical analysis, and visualization. It can be extended with more cities, longer date ranges, or additional data sources.

### 9. Limitations
The data may be modelled or forecast values rather than direct readings from official monitoring stations. Availability can vary by API response and network status. Results should be interpreted using the provider's documentation and are intended for education rather than official health or regulatory decisions.
