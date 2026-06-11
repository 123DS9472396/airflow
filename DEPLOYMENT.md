# 🚀 Cloud Deployment & Automation Guide

Once your Portfolio-Stack ELT pipeline is running perfectly on your local machine using Docker, the next logical step for a professional data engineering portfolio is taking it to the cloud. This guide outlines how to deploy Apache Airflow to the cloud and how to set up scheduled auto-refreshes for your Power BI dashboard.

---

## 🌩️ 1. Deploying Apache Airflow to the Cloud (Free / Low Cost)

To have your Airflow DAG run even when your PC is turned off, you need to host it on a cloud server.

### Option A: AWS EC2 (AWS Free Tier)
This is the most common approach for data engineers.
1. Sign up for an AWS Account (you get 12 months of Free Tier).
2. Launch an **EC2 Instance** (choose `t2.micro` which is free).
3. SSH into your instance.
4. Install Docker and Docker Compose on the instance.
5. Clone your GitHub repository onto the EC2 instance.
6. Run `docker-compose up -d` just like you did locally.
7. *Note:* Make sure to open port 8080 in your AWS Security Group so you can access the Airflow UI from your browser!

### Option B: Astronomer (Astro) or Google Cloud Composer
For a fully managed Airflow experience (no server maintenance):
- **Astronomer** offers a managed Airflow platform. You can install the Astro CLI, initialize an Astro project, copy your `dags/` and `requirements.txt` over, and deploy it to their cloud.
- **Google Cloud Composer** is GCP's managed Airflow. (Note: These options usually do not have a perpetual free tier, but are great for enterprise environments).

### Option C: Render / Heroku
You can deploy your `docker-compose` setup or Dockerfile to PaaS providers like Render or Heroku, though you may need to adjust the database configuration to use their managed PostgreSQL add-ons.

---

## 🔄 2. Power BI Scheduled Refresh

If you want your Power BI dashboard to automatically show the latest data every morning without you having to click "Refresh" manually, you need to use the Power BI Service and a Gateway.

### Step 1: Publish to Power BI Service
1. In Power BI Desktop, click **File > Publish > Publish to Power BI**.
2. Sign in with your Power BI account and publish it to "My Workspace".
3. Log in to `app.powerbi.com` to view your dashboard online.

### Step 2: Install Power BI Standard Gateway
Since your PostgreSQL database is currently running locally on your PC (or on an EC2 instance without public database access), Power BI Service (in the cloud) cannot reach it directly.
1. Download the **Power BI On-premises data gateway (standard mode)** from Microsoft.
2. Install it on the machine where your PostgreSQL database is running (e.g., your local PC or your EC2 instance).
3. Sign in to the Gateway using your Power BI credentials.

### Step 3: Configure the Dataset Connection
1. In Power BI Service, go to **Settings > Manage connections and gateways**.
2. Add a new Data Source under your Gateway.
3. Choose **PostgreSQL** as the connection type.
4. Enter your database credentials (`localhost` or server IP, database name, username, and password).

### Step 4: Schedule the Refresh
1. Go to your Workspace, find your dataset, and click the **Schedule Refresh** icon.
2. Toggle "Keep your data up to date" to **On**.
3. Set the refresh frequency to **Daily**.
4. Set the time to a few hours *after* your Airflow DAG runs (e.g., if Airflow runs at midnight, schedule Power BI refresh for 3:00 AM).
5. Click **Apply**.

🎉 Your dashboard will now automatically pull fresh data every single day!
