# GitHub AI Repository Analytics

A comprehensive data pipeline and analytics dashboard for GitHub AI/ML repositories. This project demonstrates end-to-end data engineering skills including data collection, ETL pipelines, data warehousing, API development, and interactive visualizations.

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  GitHub API │────▶│ Data Collector│────▶│  Data Lake  │────▶│  ETL Pipeline │────▶│ Data Warehouse│
│  (GraphQL)  │     │   (Python)    │     │  (MinIO/S3) │     │    (dbt)      │     │ (PostgreSQL) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘     └────────────┘
                                                                                          │
                                                                                          ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Dashboard │◀────│    API       │◀────│   Cache     │◀────│  Analytics   │◀────│   Marts    │
│  (Next.js)  │     │  (FastAPI)   │     │   (Redis)   │     │   Queries    │     │  (dbt)     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘     └────────────┘
```

## 🚀 Features

### Data Collection
- **Repository Discovery**: Searches GitHub for AI/ML repositories using topics and keywords
- **Comprehensive Metrics**: Collects stars, forks, issues, PRs, commits, contributors, releases
- **Rate Limit Handling**: Intelligent rate limiting with exponential backoff
- **Incremental Updates**: Only fetches new/changed data

### Data Pipeline
- **Modern Stack**: dbt for transformations, PostgreSQL for warehousing
- **Layered Architecture**: Raw → Staging → Intermediate → Marts
- **Data Quality**: Automated tests and validation checks
- **Orchestration**: Apache Airflow for scheduling and monitoring

### Analytics API
- **RESTful Endpoints**: Repository details, activity, contributors, health metrics
- **Caching**: Redis-backed caching for sub-200ms response times
- **Filtering & Pagination**: Flexible query parameters
- **OpenAPI Docs**: Auto-generated Swagger/ReDoc documentation

### Dashboard
- **Real-time Visualizations**: Interactive charts with Recharts
- **Key Metrics**: Repository growth, contributor activity, language trends
- **Responsive Design**: Works on desktop and mobile
- **Dark Mode**: Full dark/light theme support

## 📊 Key Metrics Tracked

| Category | Metrics |
|----------|---------|
| **Repository Growth** | Stars, forks, watchers over time |
| **Activity** | Commits, PRs, issues per day/week/month |
| **Contributors** | New vs returning, contribution patterns, bus factor |
| **Languages** | Popularity trends, language distribution |
| **Topics** | ML frameworks, domains (NLP, CV, RL, LLMs) |
| **Health** | Issue resolution time, PR merge rate, release frequency |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Data Collection** | Python 3.12, httpx, GitHub GraphQL API |
| **Orchestration** | Apache Airflow |
| **Storage** | PostgreSQL 16, MinIO (S3-compatible) |
| **Transformation** | dbt (data build tool) |
| **API** | FastAPI, asyncpg, SQLAlchemy 2.0 |
| **Cache** | Redis 7 |
| **Frontend** | Next.js 14, React 18, TypeScript |
| **Charts** | Recharts |
| **Styling** | Tailwind CSS |
| **State** | TanStack Query, Zustand |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

## 📁 Project Structure

```
github-ai-analytics/
├── docker-compose.yml           # Local development stack
├── .env.example                 # Environment variables template
├── PROJECT_PLAN.md              # Detailed project plan
├── README.md                    # This file
│
├── data-collector/              # Python data collection service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── config.py            # Configuration management
│       ├── github_client.py     # GitHub API client
│       ├── database.py          # Database operations
│       ├── models/              # Pydantic models
│       ├── collectors/          # Data collectors
│       └── main.py              # CLI entry point
│
├── etl-pipeline/                # dbt transformation pipeline
│   ├── dbt_project/
│   │   ├── dbt_project.yml
│   │   ├── models/
│   │   │   ├── staging/         # Cleaned raw data
│   │   │   ├── intermediate/    # Business logic
│   │   │   └── marts/           # Analytics-ready tables
│   │   └── macros/              # Reusable SQL macros
│   └── airflow/
│       └── dags/                # Airflow DAGs
│
├── api/                         # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── config.py
│       ├── database.py
│       ├── cache.py
│       ├── models/              # Pydantic response models
│       ├── routers/             # API endpoints
│       └── main.py              # Application entry point
│
├── dashboard/                   # Next.js frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── src/
│       ├── app/                 # App Router pages
│       ├── components/          # React components
│       ├── hooks/               # Custom hooks
│       ├── lib/                 # Utilities
│       └── types/               # TypeScript types
│
└── infrastructure/              # Infrastructure configs
    ├── postgres/
    │   └── init.sql             # Database initialization
    └── minio/
        └── buckets.json         # MinIO bucket config
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- GitHub Personal Access Token (with `repo` and `read:org` scopes)
- 8GB+ RAM recommended

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/github-ai-analytics.git
cd github-ai-analytics

# Copy environment template
cp .env.example .env

# Edit .env with your GitHub token and secure passwords
# Required: GITHUB_TOKEN, POSTGRES_PASSWORD, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
```

### 2. Start the Stack

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **API Health** | http://localhost:8000/health | - |
| **Airflow** | http://localhost:8080 | airflow/airflow |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **PostgreSQL** | localhost:5432 | analytics/secure_password |

### 4. Run Initial Data Collection

```bash
# Trigger manual collection
docker-compose exec data-collector python -m src.main collect-all

# Or trigger via Airflow UI at http://localhost:8080
```

## 📖 API Endpoints

### Repositories
```
GET /api/v1/repositories                    # List repositories (paginated, filtered)
GET /api/v1/repositories/{id}               # Repository details
GET /api/v1/repositories/{id}/activity      # Activity timeline
GET /api/v1/repositories/{id}/contributors  # Top contributors
GET /api/v1/repositories/{id}/health        # Health metrics
```

### Analytics
```
GET /api/v1/analytics/languages             # Language trends
GET /api/v1/analytics/topics                # Topic trends
GET /api/v1/analytics/leaderboard           # Contributor leaderboard
GET /api/v1/analytics/summary               # Dashboard summary
```

### Example Queries

```bash
# Top 10 Python AI repos by stars
curl "http://localhost:8000/api/v1/repositories?language=Python&is_ai_ml=true&sort_by=stargazers_count&per_page=10"

# Repository activity for last 30 days
curl "http://localhost:8000/api/v1/repositories/1/activity?start_date=2024-01-01&end_date=2024-01-31"

# Monthly contributor leaderboard
curl "http://localhost:8000/api/v1/analytics/leaderboard?period_type=monthly&limit=20"
```

## 🔧 Development

### Running Services Individually

```bash
# Data Collector
cd data-collector
pip install -r requirements.txt
python -m src.main collect-repos

# API
cd api
pip install -r requirements.txt
uvicorn src.main:app --reload

# Dashboard
cd dashboard
npm install
npm run dev

# dbt
cd etl-pipeline/dbt_project
dbt run
dbt test
```

### Running Tests

```bash
# All tests via Docker
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

# Or individually
cd data-collector && pytest
cd api && pytest
cd dashboard && npm test
cd etl-pipeline/dbt_project && dbt test
```

## 📈 Data Models

### Core Tables (Marts)

| Table | Description | Grain |
|-------|-------------|-------|
| `dim_repository` | Repository attributes | One per repository |
| `dim_contributor` | Contributor profiles | One per contributor |
| `dim_date` | Date dimension | One per day |
| `fct_repository_activity` | Daily activity metrics | Repo × Day |
| `fct_contributor_activity` | Contributor daily activity | Contributor × Day |
| `fct_repository_health` | Health scores | One per repository |
| `agg_language_trends` | Language popularity over time | Language × Day |
| `agg_topic_trends` | AI/ML topic trends | Topic × Day |
| `agg_contributor_leaderboard` | Top contributors | Contributor × Period |

## 🔐 Security

- **Secrets Management**: All secrets via environment variables
- **Rate Limiting**: API rate limiting (100 req/min default)
- **CORS**: Configurable allowed origins
- **Non-root Containers**: All containers run as non-root users
- **Network Isolation**: Docker network segmentation

## 📦 Deployment

### Production Checklist

- [ ] Use managed PostgreSQL (RDS, Cloud SQL)
- [ ] Use managed Redis (ElastiCache, Memorystore)
- [ ] Use object storage (S3, GCS) instead of MinIO
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation (ELK, Loki)
- [ ] Set up backup strategies
- [ ] Configure autoscaling for API/dashboard
- [ ] Use Airflow on managed service (MWAA, Cloud Composer)

### Kubernetes Deployment

```bash
# Build and push images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml push

# Deploy with Helm (create your own charts)
helm install github-ai-analytics ./helm-chart
```

## 🧪 Testing Strategy

| Test Type | Tools | Coverage Target |
|-----------|-------|-----------------|
| Unit Tests | pytest, Jest | 80%+ |
| Integration Tests | pytest-asyncio, Testcontainers | Key flows |
| Contract Tests | Pact | API contracts |
| Data Tests | dbt tests | All models |
| E2E Tests | Playwright | Critical paths |

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GitHub REST/GraphQL API](https://docs.github.com/en/rest)
- [dbt](https://www.getdbt.com/) for transformation framework
- [FastAPI](https://fastapi.tiangolo.com/) for modern Python APIs
- [Next.js](https://nextjs.org/) for React framework
- [Recharts](https://recharts.org/) for composable charts
- [Tailwind CSS](https://tailwindcss.com/) for utility-first styling

## 📞 Contact

For questions or suggestions, please open an issue or contact:
- **Author**: Shivam Chaudhari
- **Email**: Shivamc4505@gmail.com


---

⭐ **Star this repo if you find it useful for your learning or projects!**
