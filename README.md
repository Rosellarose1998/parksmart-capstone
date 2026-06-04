# ParkSmart

**Smart Parking Management System** — backend API by ParkWise Solutions.

ParkSmart helps drivers locate, reserve, and manage parking spaces online. Administrators monitor availability, manage users, and view reservation activity through a REST API.

## Architecture

```
┌─────────────┐     HTTPS      ┌──────────────┐     Private IP    ┌─────────────┐
│   Client    │ ──────────────▶│  Cloud Run   │ ────────────────▶ │  Cloud SQL  │
│  (Frontend) │                │  (Flask)     │                   │ (PostgreSQL)│
└─────────────┘                └──────────────┘                   └─────────────┘
                                      │
                                      ▼
                               Secret Manager
                            (JWT secret, DB password)
```

| Component | Technology |
|-----------|------------|
| API | Python 3.12, Flask, SQLAlchemy |
| Database | Google Cloud SQL (PostgreSQL 16) |
| Auth | JWT + bcrypt password hashing |
| Containers | Docker (`python:3.12-slim-bookworm`, multi-stage, non-root) |
| Infrastructure | Terraform (GCP) |
| CI/CD | GitHub Actions |

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/register` | Create account | Public |
| POST | `/api/v1/auth/login` | Login, get JWT | Public |
| GET | `/api/v1/auth/me` | Current user profile | User |
| GET | `/api/v1/parking/lots` | List parking lots | Public |
| GET | `/api/v1/parking/spots` | List spots (filter by status/lot) | Public |
| POST | `/api/v1/reservations` | Reserve a spot | User |
| GET | `/api/v1/reservations/me` | My reservations | User |
| POST | `/api/v1/reservations/{id}/cancel` | Cancel reservation | User |
| GET | `/api/v1/admin/dashboard` | Admin stats | Admin |
| GET | `/api/v1/admin/users` | List users | Admin |
| POST | `/api/v1/admin/seed` | Seed demo data | Admin |
| GET | `/health` | Health check | Public |

API base path: `/api/v1`. All endpoints return JSON.

## Local Development

### Prerequisites

- Python 3.12+
- Docker & Docker Compose

### Quick start with Docker

```bash
cd backend
docker compose up --build
```

API available at `http://localhost:8080`. Docs at `http://localhost:8080/docs`.

### Manual setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Start PostgreSQL (or use docker compose up db)
docker compose up db -d

# Run migrations
alembic upgrade head

# Start API
gunicorn --bind 0.0.0.0:8080 --reload app.main:app
```

### Run tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## GCP Deployment

### 1. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GCP project ID and GitHub repo
```

### 2. Provision infrastructure

```bash
terraform init
terraform plan
terraform apply
```

This creates:
- Cloud SQL PostgreSQL instance (private IP, VPC peering)
- Cloud Run service with Secret Manager integration
- Artifact Registry repository
- IAM service accounts (least-privilege)
- Workload Identity Federation for GitHub Actions

### 3. Configure GitHub Secrets

After `terraform apply`, set these in your GitHub repository:

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Output: `workload_identity_provider` |
| `GCP_SERVICE_ACCOUNT` | Output: `ci_service_account` |
| `SNYK_TOKEN` | API token from [Snyk Account Settings](https://app.snyk.io/account) (required for Snyk workflow) |

### 4. Deploy

Push to `main` triggers the deploy workflow, or run manually via **Actions → Deploy → Run workflow**.

## Security

- Passwords hashed with bcrypt
- JWT tokens for stateless auth
- Secrets stored in GCP Secret Manager (never in code or env files committed to git)
- Cloud SQL on private IP only (no public access)
- IAM roles scoped per service account
- Container vulnerability scanning via Trivy and Snyk in CI
- Snyk scans: Python dependencies, Docker images, Terraform IaC (results in GitHub **Security** tab)
- Non-root Docker user

## Project Structure

```
ParkSmart/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Flask app factory
│   │   ├── main.py             # WSGI entry point
│   │   ├── config.py           # Settings from environment
│   │   ├── database.py         # SQLAlchemy + Google Cloud SQL connector
│   │   ├── models/             # Database models
│   │   ├── blueprints/         # Flask route blueprints
│   │   ├── services/           # Business logic
│   │   └── utils/              # Auth utilities
│   ├── alembic/                # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── docker-compose.yml
├── terraform/                  # GCP infrastructure
└── .github/workflows/          # CI/CD pipelines
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (local dev) | Local |
| `CLOUD_SQL_CONNECTION_NAME` | Cloud SQL instance connection name | GCP |
| `DB_USER` | Database username | GCP |
| `DB_PASSWORD` | Database password | GCP |
| `DB_NAME` | Database name | GCP |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens | Yes |
| `CORS_ORIGINS` | JSON array of allowed origins | Yes |
| `DEBUG` | Enable debug mode | No |
