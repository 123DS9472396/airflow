-- models/marts/mart_city_weather.sql
-- GOLD LAYER: Business-ready city weather summary for Power BI dashboard

{{ config(
    materialized='table',
    description='City-level weather summary. Gold layer. Refreshed daily by Airflow.'
) }}

WITH daily_stats AS (
    SELECT
        city_name,
        country_code,
        DATE(data_collected_at)                     AS weather_date,

        -- Temperature KPIs
        ROUND(AVG(temperature_celsius), 1)          AS avg_temp_c,
        ROUND(MAX(temperature_celsius), 1)          AS max_temp_c,
        ROUND(MIN(temperature_celsius), 1)          AS min_temp_c,
        ROUND(AVG(feels_like_celsius), 1)           AS avg_feels_like_c,

        -- Humidity KPIs
        ROUND(AVG(humidity_percent), 0)             AS avg_humidity_pct,
        MAX(humidity_percent)                        AS max_humidity_pct,

        -- Wind KPIs
        ROUND(AVG(wind_speed_kmh), 1)               AS avg_wind_kmh,
        ROUND(MAX(wind_speed_kmh), 1)               AS max_wind_kmh,

        -- Visibility
        ROUND(AVG(visibility_km), 1)                AS avg_visibility_km,

        -- Conditions
        MODE() WITHIN GROUP (ORDER BY weather_condition)                     AS dominant_condition,
        ROUND(AVG(cloud_cover_percent), 0)          AS avg_cloud_cover_pct,

        -- Daylight
        AVG(daylight_minutes)                       AS avg_daylight_minutes,

        -- Data freshness
        MAX(data_collected_at)                      AS last_updated_at,
        COUNT(*)                                    AS record_count

    FROM {{ ref('stg_weather') }}
    GROUP BY city_name, country_code, weather_date
),

with_comfort_index AS (
    SELECT
        *,
        -- Heat Index calculation (simplified Steadman formula)
        ROUND(
            -8.78469475556 
            + (1.61139411 * avg_temp_c)
            + (2.33854883889 * avg_humidity_pct / 100)
            - (0.14611605 * avg_temp_c * avg_humidity_pct / 100)
            - (0.012308094 * avg_temp_c * avg_temp_c)
            - (0.0164248277778 * (avg_humidity_pct/100) * (avg_humidity_pct/100))
            + (0.002211732 * avg_temp_c * avg_temp_c * avg_humidity_pct/100)
            + (0.00072546 * avg_temp_c * (avg_humidity_pct/100) * (avg_humidity_pct/100))
            - (0.000003582 * avg_temp_c * avg_temp_c * (avg_humidity_pct/100) * (avg_humidity_pct/100))
        , 1) AS heat_index_c,

        -- Comfort classification
        CASE
            WHEN avg_temp_c < 15 THEN 'Cold'
            WHEN avg_temp_c BETWEEN 15 AND 22 THEN 'Cool & Pleasant'
            WHEN avg_temp_c BETWEEN 22 AND 28 THEN 'Warm & Comfortable'
            WHEN avg_temp_c BETWEEN 28 AND 35 THEN 'Hot'
            ELSE 'Extreme Heat'
        END AS comfort_category,

        -- Wind classification
        CASE
            WHEN avg_wind_kmh < 5  THEN 'Calm'
            WHEN avg_wind_kmh < 20 THEN 'Light Breeze'
            WHEN avg_wind_kmh < 40 THEN 'Moderate Wind'
            WHEN avg_wind_kmh < 60 THEN 'Strong Wind'
            ELSE 'Storm'
        END AS wind_category

    FROM daily_stats
)

SELECT * FROM with_comfort_index
