# Enterprise Log Intelligence & Predictive System Monitoring Platform

**Project ID:** PY-W4-009  
**Organization:** AB INFOTECH SOLUTIONS PVT LTD  
**Project Type:** Python Backend Development & Data Analytics  
**Week:** 4

## 1. Project Overview

The Enterprise Log Intelligence & Predictive System Monitoring Platform is a Python-based application designed to collect, process, analyze, and monitor application logs from different services.

The system identifies recurring errors, detects unusual activities, monitors service health, and manages incidents through a centralized dashboard and REST APIs.

## 2. Project Objectives

- Collect application logs from different sources.
- Parse and validate log records.
- Identify duplicate and invalid records.
- Analyze service performance and error rates.
- Detect unusual patterns using rule-based techniques and Machine Learning.
- Automatically create and manage incidents.
- Display monitoring results through a Streamlit dashboard.
- Provide REST API endpoints using FastAPI.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical operations |
| FastAPI | REST API development |
| Streamlit | Interactive dashboard |
| SQLAlchemy | Database operations |
| SQLite | Database storage |
| Scikit-learn | Anomaly detection |
| Matplotlib | Data visualization |
| Pytest | Testing |

## 4. Main Project Modules

### Module 1: Log Ingestion & Parsing
- Supports CSV, JSON and TXT parsing.
- Validates required log fields.
- Normalizes timestamps.
- Removes duplicate records.
- Separates invalid records.

### Module 2: Service Health & Performance Analytics
- Calculates total logs.
- Calculates error and warning counts.
- Measures error rates.
- Calculates average response time.
- Displays service health status.

### Module 3: Intelligent Anomaly Detection
- Identifies high error rates.
- Detects high response times.
- Uses Isolation Forest for unusual service behavior.
- Generates anomaly information.

### Module 4: Incident Management
- Creates incidents from detected anomalies.
- Assigns incident severity.
- Supports Open, Investigating, Resolved and Closed statuses.
- Maintains investigation notes and audit history.
- Prevents duplicate active incidents for the same service.

### Module 5: REST API & Database
- Provides FastAPI endpoints.
- Stores logs, services and incidents.
- Supports retrieving and filtering records.
- Uses SQLAlchemy and SQLite.

### Module 6: Monitoring Dashboard
- Displays system overview.
- Shows service performance analytics.
- Displays incidents and their statuses.
- Provides live log filtering.
- Includes a Run Anomaly Detection feature.

## 5. Project Structure

```text
Week4_Project/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── schemas/
│   ├── core/
│   ├── ingestion/
│   ├── analytics/
│   ├── incidents/
│   ├── database/
│   └── main.py
│
├── dashboard/
│   ├── app.py
│   └── app_backup.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── reports/
├── scripts/
├── tests/
├── docs/
├── screenshots/
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── Dockerfile
```

## 6. Installation & Execution

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Import sample logs into the database

```bash
python -m scripts.import_logs_to_db
```

### Step 3: Start FastAPI backend

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

### Step 4: Open Swagger documentation

http://127.0.0.1:8000/docs

### Step 5: Start Streamlit dashboard

Open a second terminal and execute:

```bash
python -m streamlit run dashboard/app.py
```

Dashboard URL:

http://localhost:8501

## 7. Important API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/logs/` | Retrieve logs |
| POST | `/logs/` | Add a log |
| GET | `/services/` | Retrieve service analytics |
| GET | `/services/{service_name}` | View service details |
| GET | `/incidents/` | Retrieve incidents |
| POST | `/incidents/` | Create an incident |
| POST | `/incidents/detect-anomalies` | Detect anomalies and create incidents |
| PATCH | `/incidents/{incident_id}/status` | Update incident status |

## 8. Database

The project uses SQLite for initial database storage.

Main database tables:

- Services
- Logs
- Incidents
- Audit History

Database file: `data/monitoring.db`

## 9. Machine Learning

The project uses the Isolation Forest algorithm from Scikit-learn for detecting unusual service behavior.

Rule-based detection also identifies services with high error rates and high average response times.

**Note:** The current sample dataset is synthetic and small. Machine Learning results are experimental and should not be treated as production predictions.

## 10. Screenshots

Project screenshots are stored in the `screenshots/` folder.

They include:

- Dashboard Overview
- Anomaly Detection Results
- Advanced Analytics
- Service Health
- Incident Management
- Live Logs
- Swagger API Documentation
- API Testing Results

## 11. Project Outcome

The project demonstrates an integrated log monitoring system that combines Python data processing, service analytics, anomaly detection, incident management, database operations, REST APIs, and interactive visualization.

It helps demonstrate how application monitoring and incident investigation workflows can be automated.

## 12. Conclusion

The Enterprise Log Intelligence & Predictive System Monitoring Platform provides a centralized approach to application log analysis and service monitoring.

Through this project, practical knowledge of Python, FastAPI, SQLAlchemy, SQLite, Pandas, Scikit-learn, Streamlit, REST APIs, and modular software development has been applied.

---

**Developed as part of the Week 4 Internship Project**  
**AB INFOTECH SOLUTIONS PVT LTD**
