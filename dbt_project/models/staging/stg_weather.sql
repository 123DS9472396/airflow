-- models/staging/stg_weather.sql
-- SILVER LAYER: Clean, type-cast, deduplicate raw data

{{ config(
    materialized='view',
    description='Cleaned and typed view of raw weather data. Silver layer.'
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_weather') }}
),

cleaned AS (
    SELECT
        -- Keys
        INGESTION_ID,
        DATA_COLLECTED_AT,

        -- Dimensions
        UPPER(TRIM(CITY))                           AS city_name,
        UPPER(TRIM(COUNTRY))                        AS country_code,
        INITCAP(WEATHER_MAIN)                       AS weather_condition,
        LOWER(WEATHER_DESC)                         AS weather_description,

        -- Temperature metrics (cast + validate)
        ROUND(TEMPERATURE_C::NUMERIC, 2)              AS temperature_celsius,
        ROUND(FEELS_LIKE_C::NUMERIC, 2)               AS feels_like_celsius,
        ROUND((TEMPERATURE_C::NUMERIC * 9/5) + 32, 2)        AS temperature_fahrenheit,

        -- Atmospheric metrics
        HUMIDITY_PCT::INTEGER                        AS humidity_percent,
        PRESSURE_HPA::INTEGER                        AS pressure_hpa,
        CLOUD_COVER_PCT::INTEGER                     AS cloud_cover_percent,

        -- Wind metrics
        ROUND(WIND_SPEED_MS::NUMERIC, 2)              AS wind_speed_ms,
        ROUND(WIND_SPEED_MS::NUMERIC * 3.6, 2)               AS wind_speed_kmh,  -- convert m/s → km/h
        WIND_DIRECTION::INTEGER                      AS wind_direction_deg,

        -- Visibility
        VISIBILITY_M::INTEGER                        AS visibility_meters,
        ROUND(VISIBILITY_M::NUMERIC / 1000.0, 2)             AS visibility_km,

        -- Time dimensions
        SUNRISE_UTC::TIMESTAMP                   AS sunrise_utc,
        SUNSET_UTC::TIMESTAMP                    AS sunset_utc,
        EXTRACT(EPOCH FROM (SUNSET_UTC - SUNRISE_UTC))/60 AS daylight_minutes,

        -- Data quality flag
        CASE 
            WHEN TEMPERATURE_C BETWEEN -10 AND 60 
             AND HUMIDITY_PCT BETWEEN 0 AND 100
             AND WIND_SPEED_MS >= 0
            THEN TRUE 
            ELSE FALSE 
        END AS is_valid_record

    FROM source
    WHERE DATA_COLLECTED_AT IS NOT NULL
),

deduplicated AS (
    -- Remove duplicate records for the same city in the same ingestion batch
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY city_name, ingestion_id
               ORDER BY data_collected_at DESC
           ) AS row_num
    FROM cleaned
)

SELECT 
    ingestion_id, data_collected_at, city_name, country_code, weather_condition,
    weather_description, temperature_celsius, feels_like_celsius, temperature_fahrenheit,
    humidity_percent, pressure_hpa, cloud_cover_percent, wind_speed_ms, wind_speed_kmh,
    wind_direction_deg, visibility_meters, visibility_km, sunrise_utc, sunset_utc,
    daylight_minutes, is_valid_record
FROM deduplicated
WHERE row_num = 1
  AND is_valid_record = TRUE
