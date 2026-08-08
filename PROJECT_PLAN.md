# GitHub AI Repository Analytics - Data Pipeline Project

## Project Overview
A complete data pipeline that collects, processes, and visualizes analytics from GitHub AI/ML repositories. Includes automated data collection, ETL pipeline, data warehouse, and interactive web dashboard.

## Architecture
```
GitHub API → Data Collector → Raw Data Lake → ETL Pipeline → Data Warehouse → Dashboard API → Web Dashboard
                    ↓              ↓              ↓              ↓              ↓
              (Python)       (JSON/Parquet)  (dbt/SQL)    (PostgreSQL)    (FastAPI)      (React/Next.js)
```

## Tech Stack
- **Data Collection**: Python, GitHub GraphQL/REST API
- **Orchestration**: Apache Airflow or Prefect
- **Storage**: PostgreSQL (warehouse), MinIO/S3 (data lake)
- **Transformation**: dbt (data build tool) or SQL
- **API Layer**: FastAPI
- **Frontend**: Next.js + TypeScript + Tailwind CSS + Recharts
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Project Structure
```
github-ai-analytics/
├── docker-compose.yml
├── README.md
├── .env.example
├── data-collector/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── github_client.py
│   │   ├── collectors/
│   │   │   ├── repo_collector.py
│   │   │   ├── contributor_collector.py
│   │   │   ├── commit_collector.py
│   │   │   └── issue_pr_collector.py
│   │   ├── models/
│   │   └── utils/
│   └── tests/
├── etl-pipeline/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── dbt_project/
│   │   ├── models/
│   │   │   ├── staging/
│   │   │   ├── intermediate/
│   │   │   └── marts/
│   │   ├── macros/
│   │   └── dbt_project.yml
│   └── airflow/
│       ├── dags/
│       └── plugins/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── database.py
│   │   └── cache.py
│   └── tests/
├── dashboard/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   └── public/
└── infrastructure/
    ├── postgres/
    │   └── init.sql
    └── minio/
        └── buckets.json
```

## Data Models

### Raw Tables (Data Lake)
- `raw_repositories` - Repository metadata
- `raw_contributors` - Contributor information
- `raw_commits` - Commit history
- `raw_issues` - Issues data
- `raw_pull_requests` - PR data
- `raw_releases` - Release information
- `raw_stargazers` - Star history

### Staging Models (Cleaned)
- `stg_repositories`
- `stg_contributors`
- `stg_commits`
- `stg_issues`
- `stg_pull_requests`

### Marts (Analytics Ready)
- `dim_repository` - Repository dimension
- `dim_contributor` - Contributor dimension
- `dim_date` - Date dimension
- `fct_repository_activity` - Daily activity facts
- `fct_contributor_activity` - Contributor activity facts
- `fct_repository_health` - Repository health metrics
- `agg_language_trends` - Language popularity over time
- `agg_topic_trends` - AI/ML topic trends
- `agg_contributor_leaderboard` - Top contributors

## Key Metrics to Track
1. **Repository Growth**: Stars, forks, watchers over time
2. **Activity**: Commits, PRs, issues per day/week/month
3. **Contributor Analytics**: New vs returning contributors, contribution patterns
4. **Language Trends**: Popular languages in AI repos
5. **Topic Analysis**: ML frameworks, domains (NLP, CV, RL, etc.)
6. **Health Metrics**: Issue resolution time, PR merge rate, release frequency
7. **Community**: Discussions, dependencies, dependents

## API Endpoints
- `GET /api/v1/repositories` - List repositories with filters
- `GET /api/v1/repositories/{id}` - Repository details
- `GET /api/v1/repositories/{id}/activity` - Activity timeline
- `GET /api/v1/repositories/{id}/contributors` - Top contributors
- `GET /api/v1/repositories/{id}/health` - Health metrics
- `GET /api/v1/analytics/languages` - Language trends
- `GET /api/v1/analytics/topics` - Topic trends
- `GET /api/v1/analytics/leaderboard` - Contributor leaderboard
- `GET /api/v1/analytics/summary` - Dashboard summary stats

## Dashboard Pages
1. **Overview** - Key metrics, top repos, recent activity
2. **Repositories** - Searchable table, filters, detail view
3. **Repository Detail** - Deep dive with charts
4. **Trends** - Language/topic trends over time
4. **Contributors** - Leaderboard, contributor profiles
5. **Health** - Repository health scores
6. **Settings** - Data refresh, API config

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Project setup with Docker Compose
- [ ] PostgreSQL schema design
- [ ] GitHub API client with rate limiting
- [ ] Basic data collector for repositories

### Phase 2: Data Pipeline (Week 2)
- [ ] Complete all collectors (commits, contributors, issues, PRs)
- [ ] Data lake storage (Parquet/JSON)
- [ ] dbt models for staging and marts
- [ ] Airflow DAGs for orchestration

### Phase 3: API Layer (Week 3)
- [ ] FastAPI with async PostgreSQL
- [ ] All REST endpoints
- [ ] Redis caching
- [ ] API documentation (OpenAPI)

### Phase 4: Dashboard (Week 4)
- [ ] Next.js project setup
- [ ] Overview page with key metrics
- [ ] Repository list and detail pages
- [ ] Trends and analytics pages
- [ ] Contributor leaderboard
- [ ] Responsive design with Tailwind

### Phase 5: Polish & Deploy (Week 5)
- [ ] Unit/integration tests
- [ ] GitHub Actions CI/CD
- [ ] Documentation
- [ ] Deployment configs
- [ ] Performance optimization

## GitHub Search Queries for AI Repos
```
topic:machine-learning stars:>1000
topic:deep-learning stars:>1000
topic:artificial-intelligence stars:>1000
topic:nlp stars:>500
topic:computer-vision stars:>500
topic:reinforcement-learning stars:>500
topic:llm stars:>500
topic:transformers stars:>500
language:python topic:ai stars:>1000
language:python topic:ml stars:>1000
```

## Environment Variables
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=github_analytics
POSTGRES_USER=analytics
POSTGRES_PASSWORD=secure_password
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
REDIS_HOST=redis
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_URL=http://localhost:3000
```

## Success Criteria
- [ ] Collects data from 1000+ AI repositories
- [ ] Runs automated daily via Airflow
- [ ] Dashboard loads in <2 seconds
- [ ] API responds in <200ms (cached)
- [ ] 90%+ test coverage
- [ ] Comprehensive README with architecture diagrams
- [ ] Deployed to cloud (AWS/GCP/Azure) or VPS