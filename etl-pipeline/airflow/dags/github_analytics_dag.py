# GitHub AI Repository Analytics - Airflow DAG
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
import json

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

dag = DAG(
    'github_ai_analytics_pipeline',
    default_args=default_args,
    description='GitHub AI/ML Repository Analytics Data Pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
    catchup=False,
    max_active_runs=1,
    tags=['github', 'analytics', 'ai-ml', 'data-pipeline'],
)

# Task 1: Collect repository metadata
collect_repositories = DockerOperator(
    task_id='collect_repositories',
    image='github-ai-analytics/data-collector:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main collect-repos',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'GITHUB_TOKEN': '{{ var.value.github_token }}',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'github_analytics',
        'POSTGRES_USER': 'analytics',
        'POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': '{{ var.value.minio_access_key }}',
        'MINIO_SECRET_KEY': '{{ var.value.minio_secret_key }}',
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 2: Collect contributors
collect_contributors = DockerOperator(
    task_id='collect_contributors',
    image='github-ai-analytics/data-collector:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main collect-contributors',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'GITHUB_TOKEN': '{{ var.value.github_token }}',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'github_analytics',
        'POSTGRES_USER': 'analytics',
        'POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': '{{ var.value.minio_access_key }}',
        'MINIO_SECRET_KEY': '{{ var.value.minio_secret_key }}',
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 3: Collect commits
collect_commits = DockerOperator(
    task_id='collect_commits',
    image='github-ai-analytics/data-collector:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main collect-commits',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'GITHUB_TOKEN': '{{ var.value.github_token }}',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'github_analytics',
        'POSTGRES_USER': 'analytics',
        'POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': '{{ var.value.minio_access_key }}',
        'MINIO_SECRET_KEY': '{{ var.value.minio_secret_key }}',
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 4: Collect issues and PRs
collect_issues_prs = DockerOperator(
    task_id='collect_issues_prs',
    image='github-ai-analytics/data-collector:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main collect-issues-prs',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'GITHUB_TOKEN': '{{ var.value.github_token }}',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'github_analytics',
        'POSTGRES_USER': 'analytics',
        'POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': '{{ var.value.minio_access_key }}',
        'MINIO_SECRET_KEY': '{{ var.value.minio_secret_key }}',
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 5: Collect releases and stargazers
collect_releases_stars = DockerOperator(
    task_id='collect_releases_stars',
    image='github-ai-analytics/data-collector:latest',
    api_version='auto',
    auto_remove=True,
    command='python -m src.main collect-releases-stars',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'GITHUB_TOKEN': '{{ var.value.github_token }}',
        'POSTGRES_HOST': 'postgres',
        'POSTGRES_DB': 'github_analytics',
        'POSTGRES_USER': 'analytics',
        'POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'MINIO_ENDPOINT': 'minio:9000',
        'MINIO_ACCESS_KEY': '{{ var.value.minio_access_key }}',
        'MINIO_SECRET_KEY': '{{ var.value.minio_secret_key }}',
    },
    mount_tmp_dir=False,
    dag=dag,
)

# Task 6: Run dbt transformations
run_dbt = DockerOperator(
    task_id='run_dbt_transformations',
    image='ghcr.io/dbt-labs/dbt-postgres:1.8.0',
    api_version='auto',
    auto_remove=True,
    command='dbt run --project-dir /usr/app/dbt_project --profiles-dir /root/.dbt',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'DBT_POSTGRES_HOST': 'postgres',
        'DBT_POSTGRES_PORT': '5432',
        'DBT_POSTGRES_DB': 'github_analytics',
        'DBT_POSTGRES_USER': 'analytics',
        'DBT_POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'DBT_PROFILES_DIR': '/root/.dbt',
    },
    volumes=['/opt/airflow/dbt_project:/usr/app/dbt_project'],
    mount_tmp_dir=False,
    dag=dag,
)

# Task 7: Run dbt tests
run_dbt_tests = DockerOperator(
    task_id='run_dbt_tests',
    image='ghcr.io/dbt-labs/dbt-postgres:1.8.0',
    api_version='auto',
    auto_remove=True,
    command='dbt test --project-dir /usr/app/dbt_project --profiles-dir /root/.dbt',
    docker_url='unix://var/run/docker.sock',
    network_mode='github-ai-analytics_default',
    environment={
        'DBT_POSTGRES_HOST': 'postgres',
        'DBT_POSTGRES_PORT': '5432',
        'DBT_POSTGRES_DB': 'github_analytics',
        'DBT_POSTGRES_USER': 'analytics',
        'DBT_POSTGRES_PASSWORD': '{{ var.value.postgres_password }}',
        'DBT_PROFILES_DIR': '/root/.dbt',
    },
    volumes=['/opt/airflow/dbt_project:/usr/app/dbt_project'],
    mount_tmp_dir=False,
    dag=dag,
)

# Task 8: Refresh materialized views
refresh_materialized_views = PostgresOperator(
    task_id='refresh_materialized_views',
    postgres_conn_id='postgres_github_analytics',
    sql="""
    REFRESH MATERIALIZED VIEW CONCURRENTLY marts.agg_language_trends;
    REFRESH MATERIALIZED VIEW CONCURRENTLY marts.agg_topic_trends;
    REFRESH MATERIALIZED VIEW CONCURRENTLY marts.agg_contributor_leaderboard;
    """,
    dag=dag,
)

# Task 9: Invalidate API cache
invalidate_cache = BashOperator(
    task_id='invalidate_api_cache',
    bash_command='curl -X POST http://api:8000/admin/cache/invalidate -H "Authorization: Bearer {{ var.value.api_admin_token }}"',
    dag=dag,
)

# Task 10: Data quality checks
data_quality_check = PostgresOperator(
    task_id='data_quality_check',
    postgres_conn_id='postgres_github_analytics',
    sql="""
    -- Check for minimum data volumes
    DO $$
    DECLARE
        repo_count INTEGER;
        commit_count INTEGER;
        contributor_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO repo_count FROM marts.dim_repository;
        SELECT COUNT(*) INTO commit_count FROM marts.fct_repository_activity;
        SELECT COUNT(*) INTO contributor_count FROM marts.dim_contributor;
        
        IF repo_count < 100 THEN
            RAISE EXCEPTION 'Too few repositories: %', repo_count;
        END IF;
        
        IF commit_count < 1000 THEN
            RAISE EXCEPTION 'Too few commits: %', commit_count;
        END IF;
        
        IF contributor_count < 50 THEN
            RAISE EXCEPTION 'Too few contributors: %', contributor_count;
        END IF;
        
        RAISE NOTICE 'Data quality check passed: % repos, % commits, % contributors', 
            repo_count, commit_count, contributor_count;
    END $$;
    """,
    dag=dag,
)

# Task 11: Send success notification
notify_success = BashOperator(
    task_id='notify_success',
    bash_command='''
    curl -X POST "{{ var.value.slack_webhook }}" \
        -H "Content-Type: application/json" \
        -d '{"text": "✅ GitHub AI Analytics pipeline completed successfully!", "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "*GitHub AI Analytics Pipeline* ✅ Completed successfully at {{ ts }}"}}]}'
    ''',
    dag=dag,
)

# Define task dependencies
# Collection tasks can run in parallel
[collect_repositories, collect_contributors, collect_commits, collect_issues_prs, collect_releases_stars] >> run_dbt

# dbt run -> dbt tests -> refresh views -> invalidate cache -> quality check -> notify
run_dbt >> run_dbt_tests >> refresh_materialized_views >> invalidate_cache >> data_quality_check >> notify_success