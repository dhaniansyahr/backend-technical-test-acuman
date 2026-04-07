# Customer Data Pipeline

A data pipeline with 3 Docker services that ingests customer data from a mock server into PostgreSQL.

## Architecture

```
Flask (JSON) → FastAPI (Ingest) → PostgreSQL → API Response
```

| Service          | Port | Description                          |
|------------------|------|--------------------------------------|
| mock-server      | 5000 | Flask API serving customer JSON data |
| pipeline-service | 8000 | FastAPI ingestion + query endpoints  |
| postgres         | 5432 | PostgreSQL 15 data storage           |

## Prerequisites

- Docker Desktop (running)
- Python 3.10+
- Git

Verify Docker Compose:
```bash
docker-compose --version
```

## Quick Start

```bash
# Start all services
docker-compose up -d

# Wait a few seconds for services to initialize, then ingest data
curl -X POST http://localhost:8000/api/ingest
```

## API Endpoints

### Flask Mock Server (port 5000)

| Endpoint                | Method | Description                        |
|-------------------------|--------|------------------------------------|
| `/api/customers`        | GET    | Paginated list (`page`, `limit`)   |
| `/api/customers/{id}`   | GET    | Single customer by `customer_id`   |
| `/api/health`           | GET    | Health check                       |

### FastAPI Pipeline (port 8000)

| Endpoint                | Method | Description                              |
|-------------------------|--------|------------------------------------------|
| `/api/ingest`           | POST   | Fetch from Flask & upsert into Postgres  |
| `/api/customers`        | GET    | Paginated list from DB (`page`, `limit`) |
| `/api/customers/{id}`   | GET    | Single customer from DB                  |
| `/api/health`           | GET    | Health check                             |

## Testing

```bash
# 1. Test Flask mock server
curl http://localhost:5000/api/customers?page=1&limit=5

# 2. Trigger data ingestion
curl -X POST http://localhost:8000/api/ingest

# 3. Query ingested data
curl http://localhost:8000/api/customers?page=1&limit=5

# 4. Get a single customer
curl http://localhost:8000/api/customers/CUST-001
```

## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/
    │   ├── __init__.py
    │   └── customer.py
    ├── services/
    │   ├── __init__.py
    │   └── ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Design Decisions

- **Upsert logic**: Uses PostgreSQL `ON CONFLICT DO UPDATE` so the pipeline is idempotent — running `/api/ingest` multiple times won't create duplicates.
- **Auto-pagination**: The ingestion service automatically paginates through the Flask API to fetch all records regardless of dataset size.
- **Health checks**: Docker Compose uses PostgreSQL health checks to ensure the database is ready before starting dependent services.
