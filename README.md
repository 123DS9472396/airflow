# WeatherFlow: Top 1% Enterprise Data Engineering Pipeline 🚀

**WeatherFlow** is an enterprise-grade automated Data Engineering ELT pipeline and a complete demonstration of the modern data stack (OpenWeatherMap API → Apache Airflow → PostgreSQL/Snowflake → dbt → Power BI Python Visuals).

It automatically extracts live weather and atmospheric data across 15 major Indian cities, orchestrates the entire workflow locally via Docker, transforms the raw data using a strict Medallion Architecture, and renders a stunning, data-driven Dark Mode dashboard directly inside Power BI using a custom high-DPI Python visualization script.

### 🌟 Unique Selling Propositions (What makes this Top 1%)
Most portfolio projects use static CSV files or manual execution. WeatherFlow is a fully automated, cloud-ready data ecosystem.

1. **Automated DAG Orchestration:** Completely replaces manual script execution with **Apache Airflow**. The DAG automatically runs every midnight, fetching live data, handling retries on API failure, and triggering downstream transformations.
2. **dbt Medallion Architecture:** Implements the industry-standard multi-hop architecture. Instead of messy SQL scripts, data moves from **Bronze** (Raw) → **Silver** (Cleaned, Typed, Deduplicated, Tested) → **Gold** (Pre-aggregated KPIs, Heat Indexes, Alerts).
3. **Data Observability:** Uses **dbt tests** to validate data quality (not null, accepted values) before it ever reaches the dashboard, preventing bad data from corrupting the Gold layer.
4. **Code-Driven BI Visualization:** Instead of dragging and dropping basic Power BI charts, this project uses a 300-line custom Python `matplotlib` script injected directly into a Power BI Python visual to generate a stunning, pixel-perfect 1920x1080 dashboard that Power BI alone cannot natively achieve.

---

### 📸 Dashboard Preview
*WeatherFlow — Real-Time Indian Weather Analytics Dashboard*

![Dashboard Preview](weather_dashboard_v8.png)

---

### 🏗️ Enterprise Architecture
This repository models the entire lifecycle of a Top 1% Data Engineering pipeline.

**1. Data Ingestion & Orchestration**
- **Apache Airflow (Dockerized):** Runs the `weather_pipeline.py` DAG. Uses Python operators to fetch live JSON data from the OpenWeatherMap REST API and loads it into the database.

**2. Data Storage & Transformation**
- **PostgreSQL / Snowflake:** The data warehouse where raw data lands. 
- **dbt (Data Build Tool):** Executes SQL models to build the Medallion architecture:
  - `stg_weather.sql` (🥈 Silver): Casts timestamps, converts Kelvin to Celsius, calculates daylight minutes.
  - `mart_city_weather.sql` (🥇 Gold): Calculates the simplified Steadman Heat Index, assigns comfort categories, and aggregates daily metrics.
  - `mart_weather_alerts.sql` (🥇 Gold): Flags extreme heat (>40°C), strong winds, and heavy rain.

**3. Visualization Layer**
- **Power BI Desktop:** Connects directly to the Gold tables in the data warehouse. Uses an embedded Python script (via `matplotlib`) to render the final KPI cards, grouped bar charts, and condition donuts.

---

### 📦 Project Structure
```text
weather-elt-pipeline/
├── airflow/
│   ├── docker-compose.yml       # Docker orchestration for Airflow
│   ├── requirements.txt         # Python dependencies
│   └── dags/
│       └── weather_pipeline.py  # Airflow DAG (Extract -> Load -> dbt)
│
├── dbt_project/
│   ├── dbt_project.yml          # dbt configurations
│   ├── profiles.yml             # Data Warehouse connection profiles
│   └── models/
│       ├── staging/             # 🥈 Silver Layer (stg_weather.sql + tests)
│       └── marts/               # 🥇 Gold Layer (KPIs & Alerts)
│
├── scripts/
│   └── setup_db.sql             # DDL to initialize Database schemas
│
├── .env                         # Secrets (API keys, DB passwords - GitIgnored)
├── DEPLOYMENT.md                # Cloud Deployment Guide
└── powerbi_dashboard.py         # Custom Python code for Power BI visualization
```

---

### 🚀 Quick Start (Local Deployment)

**Prerequisites:** Docker Desktop, Python 3.10+, dbt Core, Power BI Desktop.

1. **Clone & Configure:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/weather-elt-pipeline.git
   cd weather-elt-pipeline
   ```
   Create a `.env` file in the root directory and add your OpenWeather API Key.

2. **Start Airflow Orchestration:**
   ```bash
   cd airflow
   docker-compose up airflow-init
   docker-compose up -d
   ```
   Access Airflow at `http://localhost:8080` (admin/admin). Turn on the `diacto_weather_elt_pipeline` DAG.

3. **View the Dashboard:**
   Open Power BI, connect to your database's `marts` schema, add a Python Visual, and paste the code from `powerbi_dashboard.py`.

---

### ☁️ Deploying to Production (AWS Free Tier)

You can host this entire pipeline in the cloud 24/7 for **FREE** using Amazon Web Services (AWS) Free Tier. 

**Step 1: Setup AWS EC2 (The Server)**
1. Go to aws.amazon.com and create a free account.
2. Launch a new **EC2 Instance**. Select the **Ubuntu Server** OS and the `t2.micro` instance type (which is Free Tier eligible).
3. In the Security Group settings, open **Port 22** (for SSH access) and **Port 8080** (so you can view the Airflow UI from your browser).
4. Launch the instance and download your `.pem` key file.

**Step 2: Install Docker & Clone Code**
1. SSH into your EC2 instance using your terminal: `ssh -i "your-key.pem" ubuntu@your-ec2-ip-address`
2. Run standard Linux commands to install Docker and Docker-Compose.
3. Git clone your repository onto the EC2 server.

**Step 3: Run the Pipeline 24/7**
1. CD into the `/airflow` folder on your server.
2. Run `docker-compose up -d`. 
3. Your Airflow scheduler is now running in the cloud! You can close your laptop, and the pipeline will continue to fetch weather data every night at midnight.

**Step 4: Power BI Scheduled Refresh (Optional)**
To have Power BI automatically update the cloud dashboard:
1. Install the **Power BI On-premises Data Gateway** on your EC2 instance (or keep your DB hosted in a cloud DB like Snowflake/AWS RDS).
2. Publish your dashboard to the Power BI Service.
3. Configure a "Scheduled Refresh" in Power BI Service to run daily at 1:00 AM (right after Airflow completes its midnight run).

---

### 🛠️ Tech Stack
| Category | Technology |
|----------|------------|
| **Orchestration** | Apache Airflow (Docker) |
| **Data Warehouse** | PostgreSQL / Snowflake |
| **Transformation** | dbt Core (Medallion Architecture) |
| **ETL scripting** | Python, Pandas, Requests |
| **Visualization** | Power BI, Matplotlib |

---
*Built as a professional portfolio project demonstrating real-world enterprise data engineering practices.*
