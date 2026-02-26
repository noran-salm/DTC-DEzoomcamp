# Data Engineering Zoomcamp – Homework 2
<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-Cloud_DW-29B5E8?logo=snowflake&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Kestra](https://img.shields.io/badge/Kestra-Workflows-FF6B35?logo=apache-airflow&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-FFF000?logo=duckdb&logoColor=black)

</div>

## 📚 Overview

This repository contains homework assignments and solutions for the Data Engineering course, focusing on NYC Taxi data analysis using modern data engineering tools including Kestra workflows and Snowflake data warehouse.

## 🗂️ Repository Structure

```
├── README.md
├── answers-notes.md
├── docker-compose.yml
└── flows/
    ├── snowflake_kv.yaml
    ├── snowflake_permissions.yaml
    ├── snowflake_setup.yaml
    └── snowflake_taxi.yaml
```

## 🎯 Assignments Completed

### NYC Taxi Data Homework
- **File Size Analysis**: Calculated file sizes using shell commands
- **Data Aggregation**: Analyzed Yellow and Green taxi trips for 2020
- **Time-based Queries**: Extracted March 2021 trip counts
- **Timezone Configuration**: Implemented proper timezone handling in Kestra

**See detailed answers:** [answers-notes/nyc-taxi-quiz-answers.md](answers-notes.md)

### Snowflake Integration
- **snowflake_kv**: Configuration management for Snowflake connections
- **snowflake_permissions**: Database role and permission setup
- **snowflake_setup**: Automated warehouse, database, and schema creation
- **snowflake_taxi**: End-to-end pipeline for loading NYC taxi data into Snowflake

## 🛠️ Technologies Used

- **Kestra**: Workflow orchestration and automation
- **Snowflake**: Cloud data warehouse
- **Python**: Data processing and analysis
  - `pandas`: Data manipulation
  - `duckdb`: SQL queries on parquet files
- **Docker**: Containerized development environment
- **Shell Scripts**: File operations and automation
- **Parquet**: Columnar data format

## 📊 Key Findings

| Dataset | Time Period | Trip Count |
|---------|-------------|------------|
| Yellow Taxi | All of 2020 | 24,648,499 |
| Green Taxi | All of 2020 | 1,734,051 |
| Yellow Taxi | March 2021 | 1,925,152 |

## 🚀 Getting Started

### Prerequisites
```bash
# Python dependencies
pip install pandas duckdb pyarrow

# Docker (for running Kestra)
docker --version
docker-compose --version
```

### Running with Docker

**Start Kestra:**
```bash
docker-compose up -d
```

**Access Kestra UI:**
- Open browser to `http://localhost:8080`
- Navigate to Flows to run workflows

### Snowflake Workflows

The repository includes automated Snowflake workflows:

1. **snowflake_setup**: Creates warehouse, database, and schema
2. **snowflake_permissions**: Configures database roles and permissions
3. **snowflake_taxi**: Loads NYC taxi data into Snowflake tables
4. **snowflake_kv**: Manages configuration and connection settings

Run these flows in order from the Kestra UI.

## 📝 Data Sources

All data is sourced from the NYC Taxi & Limousine Commission:
- Base URL: `https://d37ci6vzurychx.cloudfront.net/trip-data/`
- Format: Parquet files
- Naming convention: `{color}_tripdata_{YYYY-MM}.parquet`

## 🔧 Workflow Configuration

### Kestra Timezone Settings

To run Kestra workflows with proper timezone:

```yaml
timezone: "America/New_York"
```

This ensures all scheduled tasks run according to New York time, including automatic DST adjustments.

### Snowflake Connection

Configure Snowflake credentials in Kestra KV store or use the `snowflake_kv` flow to set up connection parameters:

- Account
- Username
- Password
- Warehouse
- Database
- Schema

## 📌 Notes

- File sizes are reported in MiB (Mebibytes)
- All trip counts are based on row counts in parquet files
- Data covers Yellow and Green taxi trips only (excludes FHV, FHVHV)

## 👤 Author

Noran Salm

## 📅 Last Updated

February 2026

---

**Happy Data Engineering! 🚖📊**
