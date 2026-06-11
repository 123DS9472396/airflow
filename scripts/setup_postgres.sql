-- scripts/setup_postgres.sql
-- This script runs automatically when the Postgres container starts

-- 1. Create schemas (Medallion Architecture)
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- 2. Create raw table (Airflow loads here)
CREATE TABLE IF NOT EXISTS raw.raw_weather (
    city            VARCHAR(100),
    country         VARCHAR(10),
    temperature_c   FLOAT,
    feels_like_c    FLOAT,
    humidity_pct    INTEGER,
    wind_speed_ms   FLOAT,
    wind_direction  INTEGER,
    weather_main    VARCHAR(50),
    weather_desc    VARCHAR(200),
    visibility_m    INTEGER,
    pressure_hpa    INTEGER,
    cloud_cover_pct INTEGER,
    sunrise_utc     TIMESTAMP,
    sunset_utc      TIMESTAMP,
    data_collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ingestion_id    VARCHAR(50)
);
