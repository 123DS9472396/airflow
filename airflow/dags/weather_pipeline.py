# airflow/dags/weather_pipeline.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import psycopg2
import os
import uuid
import logging

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CITIES = [
    {"name": "Mumbai",    "country": "IN"},
    {"name": "Pune",      "country": "IN"},
    {"name": "Delhi",     "country": "IN"},
    {"name": "Bangalore", "country": "IN"},
    {"name": "Chennai",   "country": "IN"},
    {"name": "Hyderabad", "country": "IN"},
    {"name": "Kolkata",   "country": "IN"},
    {"name": "Ahmedabad", "country": "IN"},
    {"name": "Jaipur",    "country": "IN"},
    {"name": "Surat",     "country": "IN"},
    {"name": "Lucknow",   "country": "IN"},
    {"name": "Kanpur",    "country": "IN"},
    {"name": "Nagpur",    "country": "IN"},
    {"name": "Indore",    "country": "IN"},
    {"name": "Bhopal",    "country": "IN"},
]

DEFAULT_ARGS = {
    "owner": "dipesh_sharma",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ---------------------------------------------------------------------------
# Task 1 — Extract from OpenWeatherMap API
# ---------------------------------------------------------------------------

def extract_weather(**context):
    """
    Fetches current weather for all cities from OpenWeatherMap API.
    Pushes raw data to XCom for downstream tasks.
    """
    api_key = os.environ["OPENWEATHER_API_KEY"]
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    records = []
    ingestion_id = str(uuid.uuid4())  # unique batch ID
    
    for city in CITIES:
        try:
            params = {
                "q": f"{city['name']},{city['country']}",
                "appid": api_key,
                "units": "metric"  # Celsius
            }
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            record = {
                "city":              city["name"],
                "country":           city["country"],
                "temperature_c":     data["main"]["temp"],
                "feels_like_c":      data["main"]["feels_like"],
                "humidity_pct":      data["main"]["humidity"],
                "wind_speed_ms":     data["wind"]["speed"],
                "wind_direction":    data["wind"].get("deg", 0),
                "weather_main":      data["weather"][0]["main"],
                "weather_desc":      data["weather"][0]["description"],
                "visibility_m":      data.get("visibility", 0),
                "pressure_hpa":      data["main"]["pressure"],
                "cloud_cover_pct":   data["clouds"]["all"],
                "sunrise_utc":       datetime.utcfromtimestamp(data["sys"]["sunrise"]).isoformat(),
                "sunset_utc":        datetime.utcfromtimestamp(data["sys"]["sunset"]).isoformat(),
                "ingestion_id":      ingestion_id,
            }
            records.append(record)
            logging.info(f"Extracted weather for {city['name']}: {record['temperature_c']}°C")
            
        except Exception as e:
            logging.error(f"Failed to fetch weather for {city['name']}: {e}")
            continue
    
    logging.info(f"Extracted {len(records)} records. Batch ID: {ingestion_id}")
    context["task_instance"].xcom_push(key="weather_records", value=records)
    return len(records)


# ---------------------------------------------------------------------------
# Task 2 — Load into Postgres RAW layer (Bronze)
# ---------------------------------------------------------------------------

def load_to_postgres(**context):
    """
    Loads extracted weather records into Postgres RAW schema (Bronze layer).
    Uses psycopg2 connector with parameterized inserts.
    """
    records = context["task_instance"].xcom_pull(
        task_ids="extract_weather", key="weather_records"
    )
    
    if not records:
        logging.warning("No records to load. Skipping Postgres insert.")
        return 0
    
    conn = psycopg2.connect(
        host=os.environ.get("DW_POSTGRES_HOST", "data-warehouse"),
        user=os.environ["DW_POSTGRES_USER"],
        password=os.environ["DW_POSTGRES_PASSWORD"],
        dbname=os.environ["DW_POSTGRES_DB"],
        port=5432
    )
    
    cursor = conn.cursor()
    
    insert_sql = """
        INSERT INTO raw.raw_weather (
            city, country, temperature_c, feels_like_c, humidity_pct,
            wind_speed_ms, wind_direction, weather_main, weather_desc,
            visibility_m, pressure_hpa, cloud_cover_pct,
            sunrise_utc, sunset_utc, ingestion_id
        ) VALUES (
            %(city)s, %(country)s, %(temperature_c)s, %(feels_like_c)s,
            %(humidity_pct)s, %(wind_speed_ms)s, %(wind_direction)s,
            %(weather_main)s, %(weather_desc)s, %(visibility_m)s,
            %(pressure_hpa)s, %(cloud_cover_pct)s,
            %(sunrise_utc)s, %(sunset_utc)s, %(ingestion_id)s
        )
    """
    
    try:
        cursor.executemany(insert_sql, records)
        conn.commit()
        logging.info(f"Successfully loaded {len(records)} records into Postgres raw.raw_weather")
    except Exception as e:
        conn.rollback()
        logging.error(f"Postgres insert failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return len(records)


# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------

with DAG(
    dag_id="portfolio_weather_elt_pipeline",
    description="End-to-end ELT: OpenWeatherMap → Snowflake → dbt transforms",
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",        # runs every day at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["portfolio", "elt", "snowflake", "weather"],
) as dag:

    # Task 1 — Extract
    extract_task = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather,
        doc_md="""
        ## Extract Task
        Fetches current weather data from OpenWeatherMap API for 8 Indian cities.
        Pushes records to XCom for the load task.
        """,
    )

    # Task 2 — Load (Bronze)
    load_task = PythonOperator(
        task_id="load_to_postgres_raw",
        python_callable=load_to_postgres,
        doc_md="""
        ## Load Task (Bronze Layer)
        Inserts raw weather records into Postgres raw.raw_weather table.
        This is the Bronze layer in the Medallion Architecture.
        """,
    )

    # Task 3 — Transform (Silver + Gold via dbt)
    dbt_run_task = BashOperator(
        task_id="dbt_run_models",
        bash_command="cd /opt/airflow/dags/../dbt_project && dbt run --profiles-dir . --target prod",
        doc_md="""
        ## Transform Task (Silver + Gold Layers)
        Runs all dbt models:
        - staging/ models = Silver layer (cleaned, typed, deduplicated)
        - marts/ models   = Gold layer (business-ready aggregations)
        """,
    )

    # Task 4 — dbt tests (data quality checks)
    dbt_test_task = BashOperator(
        task_id="dbt_test_models",
        bash_command="cd /opt/airflow/dags/../dbt_project && dbt test --profiles-dir . --target prod",
        doc_md="""
        ## Test Task (Data Quality)
        Runs dbt tests to validate:
        - Not null constraints
        - Unique key constraints  
        - Accepted values validation
        - Referential integrity
        """,
    )

    # DAG dependencies (execution order)
    extract_task >> load_task >> dbt_run_task >> dbt_test_task
