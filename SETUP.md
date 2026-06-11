# Setup Instructions

## STEP 0 — Prerequisites (All Free)
1. **Snowflake Account:** Go to app.snowflake.com/en/register (Choose AWS, US-East-1).
2. **OpenWeatherMap API Key:** Go to openweathermap.org/api.
3. **Power BI Service:** Free with Microsoft account at app.powerbi.com.
4. **Software:** Install Docker Desktop, Python 3.10+, dbt Core (`pip install dbt-snowflake`), and Power BI Desktop (Windows only).

## STEP 1 — Snowflake Setup
1. Open the `scripts/setup_snowflake.sql` file.
2. Run the entire script in the Snowflake UI Worksheets.
3. Replace `<YOUR_SNOWFLAKE_USERNAME>` in the script with your username.

## STEP 2 — Configuration
1. Open the `.env` file at the root of the project.
2. Fill in your secrets (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `OPENWEATHER_API_KEY`).
3. Note: NEVER commit the `.env` file to GitHub.

## STEP 3 — Run Airflow via Docker
1. Navigate to the `airflow/` directory in your terminal.
2. Run `docker-compose up airflow-init` (first time only).
3. Run `docker-compose up -d` to start the containers.
4. Open the Airflow UI at `http://localhost:8080` (Username: admin, Password: admin).
5. Toggle ON the DAG `portfolio_weather_elt_pipeline` and trigger it.

## STEP 4 — Run dbt (Optional local test)
1. Navigate to the `dbt_project/` directory.
2. Run `dbt debug --profiles-dir .` to test the connection.
3. Run `dbt run --profiles-dir .` to run all models.
4. Run `dbt test --profiles-dir .` to test your data.
5. Generate docs with `dbt docs generate --profiles-dir .` and serve with `dbt docs serve --profiles-dir .`.

## STEP 5 — Power BI Dashboard
1. Connect Power BI to your Snowflake account (`your_account.snowflakecomputing.com`).
2. Import `MARTS.MART_CITY_WEATHER`, `MARTS.MART_WEATHER_ALERTS`, and `STAGING.STG_WEATHER`.
3. Create the DAX measures detailed in the guide and build the 3-page report.
4. Publish the report to Power BI Service to generate a live, public URL.
