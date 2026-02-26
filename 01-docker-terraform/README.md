# Data Engineering Zoomcamp – Homework 1

![Terraform](https://img.shields.io/badge/Terraform-AWS-623CE4?logo=terraform)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)

## Overview

This repository contains **Homework 1** for the Data Engineering Zoomcamp, demonstrating:
- Infrastructure provisioning with **Terraform** (AWS)
- Data analysis with **Docker** and **PostgreSQL**
- Best practices for reproducibility and security

---

## Repository Structure
```
DTC-HW1/
├── terraform-aws/        # AWS infrastructure with Terraform
├── docker/               # NYC taxi data analysis with Docker
└── README.md             # This file
```

---

## Part 1: Terraform (AWS Infrastructure)

### Resources Created
- **Amazon S3 Bucket** – Data lake storage
- **AWS Glue Database** – Metadata catalog

### Quick Start
```bash
cd terraform-aws
terraform init
terraform plan
terraform apply
```

### Cleanup
```bash
terraform destroy
```

---

## Part 2: Docker (NYC Taxi Analysis)

### Services
- **PostgreSQL** – Database (port 5433)
- **pgAdmin** – Web UI (port 8080)
- **Python 3.13** – Data analysis

### Quick Start
```bash
cd docker

# Download data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

# Start services
docker-compose up -d
```

### Access Services

| Service | URL | Credentials | Container Port | Description |
|---------|-----|-------------|----------------|-------------|
| pgAdmin | http://localhost:8080 | pgadmin@pgadmin.com / pgadmin | 80 | Database management UI |
| PostgreSQL | localhost:5433 | postgres / postgres | 5432 | Database server |
| Jupyter Notebook | http://localhost:8888 | Token from logs | 8888 | Interactive Python environment ||

**pgAdmin Connection:** Use hostname `db` (not localhost), port `5432`

### Analysis Questions

1. How many trips had `trip_distance ≤ 1 mile`?
2. Which pickup day had the longest trip distance (< 100 miles)?
3. Which pickup zone had the largest `total_amount` on Nov 18, 2025?
4. For "East Harlem North" pickups, which drop-off zone had the largest tip?

### Cleanup
```bash
docker-compose down -v
docker rmi python-bash
```

---

## Prerequisites

- **Terraform:** >= 1.5.0
- **AWS:** Account with S3 and Glue permissions
- **Docker:** Docker and Docker Compose
- **Python:** 3.13 (in container)

---

## Best Practices

✅ Infrastructure as Code  
✅ No credentials in Git  
✅ Reproducible environments  
✅ Modular structure  
✅ Documented setup  

---

## Troubleshooting

**Terraform:** Check AWS credentials with `aws sts get-caller-identity`  
**Docker:** Check ports with `docker-compose ps`  
**pgAdmin:** Use `db:5432` for PostgreSQL connection, not `localhost`  

---

## Author

**Nouran** – Data Engineering Zoomcamp  
January 2026

---

## Notes

- AWS used instead of GCP (account limitations)
- Both parts are independent
- Educational project for learning

- AWS used instead of GCP (account limitations)
- Both parts are independent
- Educational project for learning
