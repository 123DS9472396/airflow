-- models/marts/mart_weather_alerts.sql
-- GOLD LAYER: Weather anomaly alerts for Power BI alerts page

{{ config(
    materialized='table',
    description='Weather anomaly alerts based on threshold rules. Gold layer.'
) }}

WITH thresholds AS (
    SELECT
        city_name,
        weather_date,
        avg_temp_c,
        avg_humidity_pct,
        avg_wind_kmh,
        avg_visibility_km,
        dominant_condition,
        last_updated_at,

        -- Alert flags
        CASE WHEN avg_temp_c > 40 THEN TRUE ELSE FALSE END          AS is_extreme_heat,
        CASE WHEN avg_temp_c < 10 THEN TRUE ELSE FALSE END          AS is_extreme_cold,
        CASE WHEN avg_humidity_pct > 90 THEN TRUE ELSE FALSE END    AS is_high_humidity,
        CASE WHEN avg_wind_kmh > 50 THEN TRUE ELSE FALSE END        AS is_strong_wind,
        CASE WHEN avg_visibility_km < 1 THEN TRUE ELSE FALSE END    AS is_low_visibility,
        CASE WHEN dominant_condition = 'Rain' THEN TRUE ELSE FALSE END AS is_rainy

    FROM {{ ref('mart_city_weather') }}
),

alerts_generated AS (
    SELECT
        city_name,
        weather_date,
        last_updated_at,

        -- Alert severity
        CASE
            WHEN is_extreme_heat OR is_extreme_cold OR is_strong_wind THEN 'HIGH'
            WHEN is_high_humidity OR is_low_visibility THEN 'MEDIUM'
            WHEN is_rainy THEN 'LOW'
            ELSE 'NONE'
        END AS alert_severity,

        -- Alert message
        ARRAY_TO_STRING(
            ARRAY_REMOVE(
                ARRAY[
                    CASE WHEN is_extreme_heat   THEN 'Extreme heat warning (>40°C)' END,
                    CASE WHEN is_extreme_cold   THEN 'Extreme cold warning (<10°C)' END,
                    CASE WHEN is_high_humidity  THEN 'Very high humidity (>90%)' END,
                    CASE WHEN is_strong_wind    THEN 'Strong winds (>50 km/h)' END,
                    CASE WHEN is_low_visibility THEN 'Low visibility (<1 km)' END,
                    CASE WHEN is_rainy          THEN 'Rain expected' END
                ], NULL
            ), ' | '
        ) AS alert_messages,

        avg_temp_c,
        avg_humidity_pct,
        avg_wind_kmh,
        avg_visibility_km

    FROM thresholds
)

SELECT *
FROM alerts_generated
WHERE alert_severity != 'NONE'
ORDER BY weather_date DESC, alert_severity
