# ParkSmart

**Smart Parking Management System** by ParkWise Solutions.

ParkSmart helps drivers locate, reserve, and manage parking spaces online. Administrators monitor availability, manage users, update spot status, and view reservation activity through a REST API.

This repository contains the **backend API**, **GCP infrastructure (Terraform)**, and **CI/CD pipelines**. Frontend and additional integrations can be added alongside this codebase.

---

## Architecture

```
┌─────────────┐     HTTPS      ┌──────────────┐     Private IP    ┌──────────────────┐
│   Client    │ ──────────────▶│  Cloud Run   │ ────────────────▶ │ Google Cloud SQL │
│  (Frontend) │                │ Flask +      │   Cloud SQL     │   PostgreSQL 16  │
└─────────────┘                │ Gunicorn     │   Connector     └──────────────────┘
                               └──────────────┘
                                      │
                                      ▼
                               Secret Manager
                            (JWT secret, DB password)
```

| Layer | Technology |
|-------|------------|
| API | Python 3.12, **Flask**, Gunicorn, SQLAlchemy |
| Database | **Google Cloud SQL** (PostgreSQL 16) |
| Local DB | PostgreSQL 16 (Docker Compose) |
| Auth | JWT (Bearer) + bcrypt password hashing |
| Containers | Docker (`python:3.12-slim-bookworm`, multi-stage, non-root user) |
| Cloud | GCP Cloud Run, Artifact Registry, VPC, Secret Manager |
| IaC | Terraform |
| CI/CD | GitHub Actions (test, deploy, Trivy, **Snyk**) |

---

## Repository layout

```
ParkSmart/
├── backend/                 # Flask API
│   ├── app/
│   │   ├── __init__.py      # App factory
│   │   ├── main.py          # WSGI entry (gunicorn: app.main:app)
│   │   ├── config.py
│   │   ├── database.py      # SQLAlchemy + Cloud SQL Python Connector
│   │   ├── blueprints/      # auth, parking, reservations, admin
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/             # Migrations
│   ├── tests/
│   ├── Dockerfile
│   └── docker-compose.yml
├── terraform/               # GCP (Cloud SQL, Cloud Run, IAM, WIF)
└── .github/workflows/
    ├── ci.yml               # Lint, test, Trivy, Terraform validate, Docker build
    ├── deploy.yml           # Build & deploy to Cloud Run
    └── snyk.yml             # Snyk dependency, container, and IaC scans
```

---

## API reference

Base URL: `/api/v1`  
Auth header: `Authorization: Bearer <token>`

### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/register` | Create account | Public |
| POST | `/api/v1/auth/login` | Login, receive JWT | Public |
| GET | `/api/v1/auth/me` | Current user profile | User |

### Parking

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/parking/lots` | List parking lots | Public |
| POST | `/api/v1/parking/lots` | Create lot | Admin |
| GET | `/api/v1/parking/lots/{id}` | Get lot | Public |
| PATCH | `/api/v1/parking/lots/{id}` | Update lot | Admin |
| GET | `/api/v1/parking/spots` | List spots (`?lot_id=`, `?status=`, `?spot_type=`) | Public |
| POST | `/api/v1/parking/spots` | Create spot | Admin |
| GET | `/api/v1/parking/spots/{id}` | Get spot | Public |
| PATCH | `/api/v1/parking/spots/{id}` | Update spot status/type | Admin |

**Spot status:** `available`, `occupied`, `reserved`, `maintenance`  
**Spot type:** `standard`, `compact`, `handicap`, `ev`

### Reservations

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/reservations` | Create reservation | User |
| GET | `/api/v1/reservations/me` | My reservations | User |
| GET | `/api/v1/reservations` | All reservations | Admin |
| GET | `/api/v1/reservations/{id}` | Get reservation | User / Admin |
| POST | `/api/v1/reservations/{id}/cancel` | Cancel reservation | User / Admin |

### Admin

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/admin/dashboard` | Usage statistics | Admin |
| GET | `/api/v1/admin/users` | List users | Admin |
| PATCH | `/api/v1/admin/users/{id}` | Update user (role, active status) | Admin |
| POST | `/api/v1/admin/seed` | Seed demo lots/spots | Admin |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API welcome message |

---

## Local development

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- Python 3.12+ (for manual setup and tests)
- Git

### Quick start (Docker)

```bash
cd backend
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8080 |
| Health | http://localhost:8080/health |

The API container uses `python:3.12-slim-bookworm` and runs migrations on startup.

### Manual setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env      # macOS / Linux

docker compose up db -d
alembic upgrade head
gunicorn --bind 0.0.0.0:8080 --reload app.main:app
```

### Run tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Example API calls

```bash
# Register
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'

# List available spots
curl http://localhost:8080/api/v1/parking/spots?status=available
```

---

## Database

| Environment | Connection |
|-------------|------------|
| **Local** | `DATABASE_URL` → PostgreSQL in Docker Compose |
| **GCP** | `CLOUD_SQL_CONNECTION_NAME` + `DB_USER` / `DB_PASSWORD` / `DB_NAME` via [Cloud SQL Python Connector](https://github.com/GoogleCloudPlatform/cloud-sql-python) |

Migrations are managed with Alembic:

```bash
cd backend
alembic upgrade head          # apply
alembic revision -m "message" # create new migration
```

---

## Environment variables

Copy `backend/.env.example` to `backend/.env` for local development.

| Variable | Description | Local | GCP |
|----------|-------------|-------|-----|
| `DATABASE_URL` | PostgreSQL connection string | Yes | No |
| `CLOUD_SQL_CONNECTION_NAME` | `project:region:instance` | No | Yes |
| `DB_USER` | Database user | No | Yes |
| `DB_PASSWORD` | Database password | No | Yes (Secret Manager) |
| `DB_NAME` | Database name | No | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes | Yes (Secret Manager) |
| `JWT_ALGORITHM` | JWT algorithm (default `HS256`) | Optional | Optional |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | Optional | Optional |
| `CORS_ORIGINS` | JSON array of allowed origins | Yes | Yes |
| `DEBUG` | Debug mode (`true` / `false`) | Optional | Optional |

Never commit `.env`, `terraform.tfvars`, or real secrets to Git.

---

## GCP deployment

### 1. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit: project_id, github_repo, cors_origins
```

### 2. Provision infrastructure

```bash
terraform init
terraform plan
terraform apply
```

Creates:

- Cloud SQL PostgreSQL (private IP, VPC peering, backups)
- Cloud Run v2 (Flask API, Secret Manager env vars)
- Artifact Registry
- IAM service accounts (least privilege)
- Workload Identity Federation for GitHub Actions

### 3. GitHub repository secrets

| Secret | Source |
|--------|--------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `terraform output workload_identity_provider` |
| `GCP_SERVICE_ACCOUNT` | `terraform output ci_service_account` |
| `SNYK_TOKEN` | [Snyk account token](https://app.snyk.io/account) |

### 4. Deploy

- Push to **`main`** → `deploy.yml` builds the slim image and updates Cloud Run
- Or run manually: **Actions → Deploy → Run workflow**

---

## CI/CD workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | PR / push to `main`, `develop` | Ruff lint, pytest, Trivy FS + image scan, Terraform validate, Docker build (slim base check) |
| **Deploy** | Push to `main`, manual | Build `python:3.12-slim-bookworm` image → Artifact Registry → Cloud Run |
| **Snyk** | PR / push to `main`, `develop`, manual | Scan Python deps, Docker image, Terraform; upload SARIF to GitHub Security |

---

## Security

- bcrypt password hashing
- JWT Bearer authentication with role-based access (`user`, `admin`)
- GCP Secret Manager for production secrets
- Cloud SQL accessible only via private IP (VPC)
- IAM least-privilege service accounts
- Non-root container user
- Vulnerability scanning: **Trivy** (CI) and **Snyk** (dependencies, container, IaC)
- Production images use **`python:3.12-slim-bookworm` only** (enforced via Docker `ARG` and CI)

---

## Team workflow

| Role | Focus area |
|------|------------|
| **Backend** | `backend/` — API, models, migrations, tests |
| **Frontend** | Separate app; point at `http://localhost:8080` and configure `CORS_ORIGINS` |
| **GCP / DevOps** | `terraform/`, `.github/workflows/` |

Suggested Git flow:

1. Branch from `develop` (feature branches)
2. Open PR → CI + Snyk must pass
3. Merge to `main` for deployment

---

## Pushing to GitHub

```bash
git init
git add .
git status    # confirm .venv, .env, terraform.tfvars are NOT listed
git commit -m "Initial ParkSmart backend and infrastructure"
git remote add origin https://github.com/<org>/ParkSmart.git
git push -u origin main
```

Use a **private repository** unless your project requires otherwise.

---

## License

Add your project or course license here.
