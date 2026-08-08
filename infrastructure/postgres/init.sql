-- GitHub AI Repository Analytics - Database Schema
-- This script initializes the database with all required tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================
-- RAW TABLES (Data Lake Layer)
-- ============================================

-- Raw Repositories
CREATE TABLE IF NOT EXISTS raw.repositories (
    id BIGINT PRIMARY KEY,
    node_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(500) NOT NULL,
    owner_login VARCHAR(255),
    owner_type VARCHAR(50),
    owner_id BIGINT,
    description TEXT,
    homepage VARCHAR(500),
    html_url VARCHAR(500),
    api_url VARCHAR(500),
    clone_url VARCHAR(500),
    ssh_url VARCHAR(500),
    git_url VARCHAR(500),
    svn_url VARCHAR(500),
    language VARCHAR(100),
    languages_json JSONB,
    topics JSONB,
    topics_search TEXT,
    default_branch VARCHAR(100),
    license_key VARCHAR(100),
    license_name VARCHAR(255),
    license_spdx_id VARCHAR(50),
    license_url VARCHAR(500),
    is_private BOOLEAN DEFAULT FALSE,
    is_fork BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_disabled BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    has_issues BOOLEAN DEFAULT TRUE,
    has_projects BOOLEAN DEFAULT TRUE,
    has_wiki BOOLEAN DEFAULT TRUE,
    has_pages BOOLEAN DEFAULT FALSE,
    has_downloads BOOLEAN DEFAULT TRUE,
    has_discussions BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMPTZ,
    pushed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    size_kb INTEGER,
    stargazers_count INTEGER DEFAULT 0,
    watchers_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    subscribers_count INTEGER DEFAULT 0,
    network_count INTEGER DEFAULT 0,
    contributors_count INTEGER DEFAULT 0,
    releases_count INTEGER DEFAULT 0,
    commits_count INTEGER DEFAULT 0,
    dependencies_count INTEGER DEFAULT 0,
    dependents_count INTEGER DEFAULT 0,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB
);

CREATE INDEX IF NOT EXISTS idx_raw_repos_full_name ON raw.repositories(full_name);
CREATE INDEX IF NOT EXISTS idx_raw_repos_language ON raw.repositories(language);
CREATE INDEX IF NOT EXISTS idx_raw_repos_stars ON raw.repositories(stargazers_count DESC);
CREATE INDEX IF NOT EXISTS idx_raw_repos_topics_gin ON raw.repositories USING GIN(topics);
CREATE INDEX IF NOT EXISTS idx_raw_repos_collected_at ON raw.repositories(collected_at);

-- Raw Contributors
CREATE TABLE IF NOT EXISTS raw.contributors (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    contributor_id BIGINT NOT NULL,
    contributor_login VARCHAR(255) NOT NULL,
    contributor_name VARCHAR(255),
    contributor_email VARCHAR(255),
    contributor_company VARCHAR(255),
    contributor_location VARCHAR(255),
    contributor_bio TEXT,
    contributor_avatar_url VARCHAR(500),
    contributor_html_url VARCHAR(500),
    contributor_type VARCHAR(50),
    contributor_site_admin BOOLEAN DEFAULT FALSE,
    contributions_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    commit_count INTEGER DEFAULT 0,
    first_contribution_date TIMESTAMPTZ,
    last_contribution_date TIMESTAMPTZ,
    is_organization_member BOOLEAN DEFAULT FALSE,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB,
    UNIQUE(repo_id, contributor_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_contributors_repo ON raw.contributors(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_contributors_login ON raw.contributors(contributor_login);

-- Raw Commits
CREATE TABLE IF NOT EXISTS raw.commits (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    sha VARCHAR(100) NOT NULL,
    node_id VARCHAR(100),
    author_id BIGINT,
    author_login VARCHAR(255),
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_date TIMESTAMPTZ NOT NULL,
    committer_id BIGINT,
    committer_login VARCHAR(255),
    committer_name VARCHAR(255),
    committer_email VARCHAR(255),
    committer_date TIMESTAMPTZ NOT NULL,
    message TEXT,
    message_headline VARCHAR(500),
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    total_changes INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    parents_sha JSONB,
    is_merge BOOLEAN DEFAULT FALSE,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB,
    UNIQUE(repo_id, sha)
);

CREATE INDEX IF NOT EXISTS idx_raw_commits_repo ON raw.commits(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_commits_author ON raw.commits(author_login);
CREATE INDEX IF NOT EXISTS idx_raw_commits_date ON raw.commits(author_date);
CREATE INDEX IF NOT EXISTS idx_raw_commits_sha ON raw.commits(sha);

-- Raw Issues
CREATE TABLE IF NOT EXISTS raw.issues (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    issue_id BIGINT NOT NULL,
    node_id VARCHAR(100),
    number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    state_reason VARCHAR(100),
    author_id BIGINT,
    author_login VARCHAR(255),
    author_type VARCHAR(50),
    assignee_id BIGINT,
    assignee_login VARCHAR(255),
    assignees JSONB,
    labels JSONB,
    milestone_id BIGINT,
    milestone_title VARCHAR(255),
    milestone_state VARCHAR(50),
    comments_count INTEGER DEFAULT 0,
    reactions JSONB,
    is_pull_request BOOLEAN DEFAULT FALSE,
    pull_request_url VARCHAR(500),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB,
    UNIQUE(repo_id, issue_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_issues_repo ON raw.issues(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_issues_state ON raw.issues(state);
CREATE INDEX IF NOT EXISTS idx_raw_issues_author ON raw.issues(author_login);
CREATE INDEX IF NOT EXISTS idx_raw_issues_created ON raw.issues(created_at);
CREATE INDEX IF NOT EXISTS idx_raw_issues_labels_gin ON raw.issues USING GIN(labels);

-- Raw Pull Requests
CREATE TABLE IF NOT EXISTS raw.pull_requests (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    pr_id BIGINT NOT NULL,
    node_id VARCHAR(100),
    number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    draft BOOLEAN DEFAULT FALSE,
    author_id BIGINT,
    author_login VARCHAR(255),
    author_type VARCHAR(50),
    assignee_id BIGINT,
    assignee_login VARCHAR(255),
    assignees JSONB,
    reviewers JSONB,
    labels JSONB,
    milestone_id BIGINT,
    milestone_title VARCHAR(255),
    base_ref VARCHAR(255),
    base_sha VARCHAR(100),
    head_ref VARCHAR(255),
    head_sha VARCHAR(100),
    head_repo_id BIGINT,
    head_repo_full_name VARCHAR(500),
    comments_count INTEGER DEFAULT 0,
    review_comments_count INTEGER DEFAULT 0,
    commits_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    changed_files INTEGER DEFAULT 0,
    mergeable BOOLEAN,
    mergeable_state VARCHAR(50),
    merged BOOLEAN DEFAULT FALSE,
    merged_at TIMESTAMPTZ,
    merged_by_id BIGINT,
    merged_by_login VARCHAR(255),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB,
    UNIQUE(repo_id, pr_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_prs_repo ON raw.pull_requests(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_prs_state ON raw.pull_requests(state);
CREATE INDEX IF NOT EXISTS idx_raw_prs_author ON raw.pull_requests(author_login);
CREATE INDEX IF NOT EXISTS idx_raw_prs_created ON raw.pull_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_raw_prs_merged ON raw.pull_requests(merged_at);

-- Raw Releases
CREATE TABLE IF NOT EXISTS raw.releases (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    release_id BIGINT NOT NULL,
    node_id VARCHAR(100),
    tag_name VARCHAR(255) NOT NULL,
    target_commitish VARCHAR(255),
    name VARCHAR(500),
    body TEXT,
    draft BOOLEAN DEFAULT FALSE,
    prerelease BOOLEAN DEFAULT FALSE,
    author_id BIGINT,
    author_login VARCHAR(255),
    author_type VARCHAR(50),
    assets JSONB,
    tarball_url VARCHAR(500),
    zipball_url VARCHAR(500),
    html_url VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB,
    UNIQUE(repo_id, release_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_releases_repo ON raw.releases(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_releases_published ON raw.releases(published_at);

-- Raw Stargazers (for star history)
CREATE TABLE IF NOT EXISTS raw.stargazers (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES raw.repositories(id),
    user_id BIGINT NOT NULL,
    user_login VARCHAR(255) NOT NULL,
    starred_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_stargazers_repo ON raw.stargazers(repo_id);
CREATE INDEX IF NOT EXISTS idx_raw_stargazers_date ON raw.stargazers(starred_at);

-- ============================================
-- STAGING TABLES (Cleaned/Transformed)
-- ============================================

-- Staging Repositories
CREATE TABLE IF NOT EXISTS staging.repositories (
    repo_id BIGINT PRIMARY KEY,
    node_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(500) NOT NULL,
    owner_login VARCHAR(255),
    owner_type VARCHAR(50),
    owner_id BIGINT,
    description TEXT,
    homepage VARCHAR(500),
    html_url VARCHAR(500),
    language VARCHAR(100),
    languages JSONB,
    topics TEXT[],
    default_branch VARCHAR(100),
    license_key VARCHAR(100),
    license_name VARCHAR(255),
    license_spdx_id VARCHAR(50),
    is_private BOOLEAN DEFAULT FALSE,
    is_fork BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    has_issues BOOLEAN DEFAULT TRUE,
    has_projects BOOLEAN DEFAULT TRUE,
    has_wiki BOOLEAN DEFAULT TRUE,
    has_pages BOOLEAN DEFAULT FALSE,
    has_discussions BOOLEAN DEFAULT FALSE,
    pushed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    size_kb INTEGER,
    stargazers_count INTEGER DEFAULT 0,
    watchers_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    subscribers_count INTEGER DEFAULT 0,
    network_count INTEGER DEFAULT 0,
    contributors_count INTEGER DEFAULT 0,
    releases_count INTEGER DEFAULT 0,
    commits_count INTEGER DEFAULT 0,
    is_ai_ml_repo BOOLEAN GENERATED ALWAYS AS (
        topics && ARRAY['machine-learning', 'deep-learning', 'artificial-intelligence', 'nlp', 'computer-vision', 'reinforcement-learning', 'llm', 'transformers', 'ai', 'ml', 'data-science', 'neural-network', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'huggingface', 'openai', 'langchain', 'llama', 'gpt', 'bert', 'diffusion', 'gan', 'rl', 'nlp', 'cv']
    ) STORED,
    ai_ml_topics TEXT[] GENERATED ALWAYS AS (
        topics & ARRAY['machine-learning', 'deep-learning', 'artificial-intelligence', 'nlp', 'computer-vision', 'reinforcement-learning', 'llm', 'transformers', 'ai', 'ml', 'data-science', 'neural-network', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'huggingface', 'openai', 'langchain', 'llama', 'gpt', 'bert', 'diffusion', 'gan', 'rl', 'nlp', 'cv']
    ) STORED,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_repos_full_name ON staging.repositories(full_name);
CREATE INDEX IF NOT EXISTS idx_stg_repos_language ON staging.repositories(language);
CREATE INDEX IF NOT EXISTS idx_stg_repos_ai_ml ON staging.repositories(is_ai_ml_repo);
CREATE INDEX IF NOT EXISTS idx_stg_repos_topics_gin ON staging.repositories USING GIN(topics);
CREATE INDEX IF NOT EXISTS idx_stg_repos_stars ON staging.repositories(stargazers_count DESC);

-- Staging Contributors
CREATE TABLE IF NOT EXISTS staging.contributors (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES staging.repositories(repo_id),
    contributor_id BIGINT NOT NULL,
    contributor_login VARCHAR(255) NOT NULL,
    contributor_name VARCHAR(255),
    contributor_email VARCHAR(255),
    contributor_company VARCHAR(255),
    contributor_location VARCHAR(255),
    contributor_bio TEXT,
    contributor_avatar_url VARCHAR(500),
    contributor_html_url VARCHAR(500),
    contributor_type VARCHAR(50),
    contributions_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    commit_count INTEGER DEFAULT 0,
    first_contribution_date TIMESTAMPTZ,
    last_contribution_date TIMESTAMPTZ,
    is_organization_member BOOLEAN DEFAULT FALSE,
    is_bot BOOLEAN GENERATED ALWAYS AS (
        contributor_login ILIKE '%bot%' OR contributor_login ILIKE '%[bot]%' OR contributor_type = 'Bot'
    ) STORED,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, contributor_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_contributors_repo ON staging.contributors(repo_id);
CREATE INDEX IF NOT EXISTS idx_stg_contributors_login ON staging.contributors(contributor_login);
CREATE INDEX IF NOT EXISTS idx_stg_contributors_bot ON staging.contributors(is_bot);

-- Staging Commits
CREATE TABLE IF NOT EXISTS staging.commits (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES staging.repositories(repo_id),
    sha VARCHAR(100) NOT NULL,
    author_id BIGINT,
    author_login VARCHAR(255),
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_date TIMESTAMPTZ NOT NULL,
    committer_date TIMESTAMPTZ NOT NULL,
    message TEXT,
    message_headline VARCHAR(500),
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    total_changes INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    is_merge BOOLEAN DEFAULT FALSE,
    is_bot_commit BOOLEAN GENERATED ALWAYS AS (
        author_login ILIKE '%bot%' OR author_login ILIKE '%[bot]%' OR author_email ILIKE '%bot%'
    ) STORED,
    commit_date DATE GENERATED ALWAYS AS (author_date::date) STORED,
    commit_week DATE GENERATED ALWAYS AS (date_trunc('week', author_date)::date) STORED,
    commit_month DATE GENERATED ALWAYS AS (date_trunc('month', author_date)::date) STORED,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, sha)
);

CREATE INDEX IF NOT EXISTS idx_stg_commits_repo ON staging.commits(repo_id);
CREATE INDEX IF NOT EXISTS idx_stg_commits_author ON staging.commits(author_login);
CREATE INDEX IF NOT EXISTS idx_stg_commits_date ON staging.commits(author_date);
CREATE INDEX IF NOT EXISTS idx_stg_commits_commit_date ON staging.commits(commit_date);
CREATE INDEX IF NOT EXISTS idx_stg_commits_bot ON staging.commits(is_bot_commit);

-- Staging Issues
CREATE TABLE IF NOT EXISTS staging.issues (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES staging.repositories(repo_id),
    issue_id BIGINT NOT NULL,
    number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    state_reason VARCHAR(100),
    author_id BIGINT,
    author_login VARCHAR(255),
    author_type VARCHAR(50),
    assignee_login VARCHAR(255),
    labels TEXT[],
    milestone_title VARCHAR(255),
    milestone_state VARCHAR(50),
    comments_count INTEGER DEFAULT 0,
    reactions_total INTEGER DEFAULT 0,
    is_pull_request BOOLEAN DEFAULT FALSE,
    is_bot_issue BOOLEAN GENERATED ALWAYS AS (
        author_login ILIKE '%bot%' OR author_login ILIKE '%[bot]%'
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ,
    resolution_time_hours NUMERIC GENERATED ALWAYS AS (
        CASE WHEN closed_at IS NOT NULL THEN EXTRACT(EPOCH FROM (closed_at - created_at)) / 3600 END
    ) STORED,
    created_date DATE GENERATED ALWAYS AS (created_at::date) STORED,
    closed_date DATE GENERATED ALWAYS AS (closed_at::date) STORED,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, issue_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_issues_repo ON staging.issues(repo_id);
CREATE INDEX IF NOT EXISTS idx_stg_issues_state ON staging.issues(state);
CREATE INDEX IF NOT EXISTS idx_stg_issues_author ON staging.issues(author_login);
CREATE INDEX IF NOT EXISTS idx_stg_issues_created ON staging.issues(created_at);
CREATE INDEX IF NOT EXISTS idx_stg_issues_labels_gin ON staging.issues USING GIN(labels);

-- Staging Pull Requests
CREATE TABLE IF NOT EXISTS staging.pull_requests (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES staging.repositories(repo_id),
    pr_id BIGINT NOT NULL,
    number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    draft BOOLEAN DEFAULT FALSE,
    author_id BIGINT,
    author_login VARCHAR(255),
    author_type VARCHAR(50),
    assignee_login VARCHAR(255),
    labels TEXT[],
    milestone_title VARCHAR(255),
    base_ref VARCHAR(255),
    head_ref VARCHAR(255),
    comments_count INTEGER DEFAULT 0,
    review_comments_count INTEGER DEFAULT 0,
    commits_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    changed_files INTEGER DEFAULT 0,
    mergeable BOOLEAN,
    mergeable_state VARCHAR(50),
    merged BOOLEAN DEFAULT FALSE,
    merged_at TIMESTAMPTZ,
    merged_by_login VARCHAR(255),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    is_bot_pr BOOLEAN GENERATED ALWAYS AS (
        author_login ILIKE '%bot%' OR author_login ILIKE '%[bot]%'
    ) STORED,
    time_to_merge_hours NUMERIC GENERATED ALWAYS AS (
        CASE WHEN merged_at IS NOT NULL THEN EXTRACT(EPOCH FROM (merged_at - created_at)) / 3600 END
    ) STORED,
    created_date DATE GENERATED ALWAYS AS (created_at::date) STORED,
    merged_date DATE GENERATED ALWAYS AS (merged_at::date) STORED,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, pr_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_prs_repo ON staging.pull_requests(repo_id);
CREATE INDEX IF NOT EXISTS idx_stg_prs_state ON staging.pull_requests(state);
CREATE INDEX IF NOT EXISTS idx_stg_prs_author ON staging.pull_requests(author_login);
CREATE INDEX IF NOT EXISTS idx_stg_prs_created ON staging.pull_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_stg_prs_merged ON staging.pull_requests(merged_at);

-- ============================================
-- MARTS TABLES (Analytics Ready)
-- ============================================

-- Dimension: Repository
CREATE TABLE IF NOT EXISTS marts.dim_repository (
    repo_key BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL UNIQUE,
    node_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(500) NOT NULL,
    owner_login VARCHAR(255),
    owner_type VARCHAR(50),
    description TEXT,
    homepage VARCHAR(500),
    html_url VARCHAR(500),
    primary_language VARCHAR(100),
    languages JSONB,
    topics TEXT[],
    ai_ml_topics TEXT[],
    is_ai_ml_repo BOOLEAN DEFAULT FALSE,
    license_key VARCHAR(100),
    license_name VARCHAR(255),
    is_fork BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    default_branch VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    pushed_at TIMESTAMPTZ,
    size_kb INTEGER,
    stargazers_count INTEGER DEFAULT 0,
    watchers_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    subscribers_count INTEGER DEFAULT 0,
    network_count INTEGER DEFAULT 0,
    contributors_count INTEGER DEFAULT 0,
    releases_count INTEGER DEFAULT 0,
    commits_count INTEGER DEFAULT 0,
    health_score NUMERIC(5,2),
    maturity_level VARCHAR(50),
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dim_repo_full_name ON marts.dim_repository(full_name);
CREATE INDEX IF NOT EXISTS idx_dim_repo_language ON marts.dim_repository(primary_language);
CREATE INDEX IF NOT EXISTS idx_dim_repo_ai_ml ON marts.dim_repository(is_ai_ml_repo);
CREATE INDEX IF NOT EXISTS idx_dim_repo_health ON marts.dim_repository(health_score DESC);
CREATE INDEX IF NOT EXISTS idx_dim_repo_stars ON marts.dim_repository(stargazers_count DESC);

-- Dimension: Contributor
CREATE TABLE IF NOT EXISTS marts.dim_contributor (
    contributor_key BIGSERIAL PRIMARY KEY,
    contributor_id BIGINT NOT NULL UNIQUE,
    login VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(500),
    html_url VARCHAR(500),
    type VARCHAR(50),
    is_bot BOOLEAN DEFAULT FALSE,
    is_organization_member BOOLEAN DEFAULT FALSE,
    total_contributions INTEGER DEFAULT 0,
    total_repos_contributed INTEGER DEFAULT 0,
    first_contribution_date TIMESTAMPTZ,
    last_contribution_date TIMESTAMPTZ,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dim_contributor_login ON marts.dim_contributor(login);
CREATE INDEX IF NOT EXISTS idx_dim_contributor_company ON marts.dim_contributor(company);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

-- Fact: Repository Daily Activity
CREATE TABLE IF NOT EXISTS marts.fct_repository_activity (
    id BIGSERIAL PRIMARY KEY,
    repo_key BIGINT NOT NULL REFERENCES marts.dim_repository(repo_key),
    date_key DATE NOT NULL REFERENCES marts.dim_date(date_key),
    commits_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    unique_contributors INTEGER DEFAULT 0,
    issues_opened INTEGER DEFAULT 0,
    issues_closed INTEGER DEFAULT 0,
    prs_opened INTEGER DEFAULT 0,
    prs_closed INTEGER DEFAULT 0,
    prs_merged INTEGER DEFAULT 0,
    releases_published INTEGER DEFAULT 0,
    stars_gained INTEGER DEFAULT 0,
    forks_gained INTEGER DEFAULT 0,
    watchers_gained INTEGER DEFAULT 0,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_key, date_key)
);

CREATE INDEX IF NOT EXISTS idx_fct_repo_activity_repo ON marts.fct_repository_activity(repo_key);
CREATE INDEX IF NOT EXISTS idx_fct_repo_activity_date ON marts.fct_repository_activity(date_key);

-- Fact: Contributor Activity
CREATE TABLE IF NOT EXISTS marts.fct_contributor_activity (
    id BIGSERIAL PRIMARY KEY,
    contributor_key BIGINT NOT NULL REFERENCES marts.dim_contributor(contributor_key),
    repo_key BIGINT NOT NULL REFERENCES marts.dim_repository(repo_key),
    date_key DATE NOT NULL REFERENCES marts.dim_date(date_key),
    commits_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    prs_opened INTEGER DEFAULT 0,
    prs_merged INTEGER DEFAULT 0,
    issues_opened INTEGER DEFAULT 0,
    issues_closed INTEGER DEFAULT 0,
    reviews_submitted INTEGER DEFAULT 0,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(contributor_key, repo_key, date_key)
);

CREATE INDEX IF NOT EXISTS idx_fct_contrib_activity_contrib ON marts.fct_contributor_activity(contributor_key);
CREATE INDEX IF NOT EXISTS idx_fct_contrib_activity_repo ON marts.fct_contributor_activity(repo_key);
CREATE INDEX IF NOT EXISTS idx_fct_contrib_activity_date ON marts.fct_contributor_activity(date_key);

-- Fact: Repository Health Metrics
CREATE TABLE IF NOT EXISTS marts.fct_repository_health (
    repo_key BIGINT PRIMARY KEY REFERENCES marts.dim_repository(repo_key),
    -- Activity metrics
    avg_commits_per_week NUMERIC(10,2),
    avg_prs_per_week NUMERIC(10,2),
    avg_issues_per_week NUMERIC(10,2),
    active_contributors_30d INTEGER,
    active_contributors_90d INTEGER,
    -- Quality metrics
    pr_merge_rate NUMERIC(5,2),
    avg_pr_merge_time_hours NUMERIC(10,2),
    issue_resolution_rate NUMERIC(5,2),
    avg_issue_resolution_time_hours NUMERIC(10,2),
    -- Community metrics
    bus_factor INTEGER,
    core_contributors_count INTEGER,
    external_contributors_ratio NUMERIC(5,2),
    -- Release metrics
    release_frequency_days NUMERIC(10,2),
    last_release_date TIMESTAMPTZ,
    releases_last_year INTEGER,
    -- Growth metrics
    stars_growth_rate_30d NUMERIC(10,2),
    forks_growth_rate_30d NUMERIC(10,2),
    contributors_growth_rate_30d NUMERIC(10,2),
    -- Overall health score (0-100)
    health_score NUMERIC(5,2),
    health_grade VARCHAR(2),
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Aggregate: Language Trends
CREATE TABLE IF NOT EXISTS marts.agg_language_trends (
    id BIGSERIAL PRIMARY KEY,
    date_key DATE NOT NULL REFERENCES marts.dim_date(date_key),
    language VARCHAR(100) NOT NULL,
    repo_count INTEGER DEFAULT 0,
    total_stars BIGINT DEFAULT 0,
    total_forks BIGINT DEFAULT 0,
    total_commits BIGINT DEFAULT 0,
    total_contributors BIGINT DEFAULT 0,
    new_repos_count INTEGER DEFAULT 0,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date_key, language)
);

CREATE INDEX IF NOT EXISTS idx_agg_lang_trends_date ON marts.agg_language_trends(date_key);
CREATE INDEX IF NOT EXISTS idx_agg_lang_trends_lang ON marts.agg_language_trends(language);

-- Aggregate: Topic Trends
CREATE TABLE IF NOT EXISTS marts.agg_topic_trends (
    id BIGSERIAL PRIMARY KEY,
    date_key DATE NOT NULL REFERENCES marts.dim_date(date_key),
    topic VARCHAR(255) NOT NULL,
    repo_count INTEGER DEFAULT 0,
    total_stars BIGINT DEFAULT 0,
    total_forks BIGINT DEFAULT 0,
    avg_stars_per_repo NUMERIC(10,2),
    new_repos_count INTEGER DEFAULT 0,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date_key, topic)
);

CREATE INDEX IF NOT EXISTS idx_agg_topic_trends_date ON marts.agg_topic_trends(date_key);
CREATE INDEX IF NOT EXISTS idx_agg_topic_trends_topic ON marts.agg_topic_trends(topic);

-- Aggregate: Contributor Leaderboard
CREATE TABLE IF NOT EXISTS marts.agg_contributor_leaderboard (
    id BIGSERIAL PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- 'weekly', 'monthly', 'quarterly', 'yearly', 'all_time'
    contributor_key BIGINT NOT NULL REFERENCES marts.dim_contributor(contributor_key),
    rank INTEGER NOT NULL,
    total_commits INTEGER DEFAULT 0,
    total_additions INTEGER DEFAULT 0,
    total_deletions INTEGER DEFAULT 0,
    total_prs_merged INTEGER DEFAULT 0,
    total_issues_closed INTEGER DEFAULT 0,
    repos_contributed INTEGER DEFAULT 0,
    dbt_updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(period_start, period_end, period_type, contributor_key)
);

CREATE INDEX IF NOT EXISTS idx_agg_leaderboard_period ON marts.agg_contributor_leaderboard(period_start, period_end, period_type);
CREATE INDEX IF NOT EXISTS idx_agg_leaderboard_rank ON marts.agg_contributor_leaderboard(rank);

-- ============================================
-- ANALYTICS VIEWS
-- ============================================

-- Top AI/ML Repositories View
CREATE OR REPLACE VIEW analytics.top_ai_ml_repositories AS
SELECT
    dr.repo_id,
    dr.full_name,
    dr.primary_language,
    dr.ai_ml_topics,
    dr.stargazers_count,
    dr.forks_count,
    dr.contributors_count,
    dr.commits_count,
    dr.health_score,
    dr.health_grade,
    dr.created_at,
    dr.pushed_at,
    frh.active_contributors_30d,
    frh.pr_merge_rate,
    frh.issue_resolution_rate,
    frh.release_frequency_days
FROM marts.dim_repository dr
LEFT JOIN marts.fct_repository_health frh ON dr.repo_key = frh.repo_key
WHERE dr.is_ai_ml_repo = TRUE
ORDER BY dr.stargazers_count DESC;

-- Repository Activity Summary View
CREATE OR REPLACE VIEW analytics.repository_activity_summary AS
SELECT
    dr.repo_id,
    dr.full_name,
    dr.primary_language,
    dr.is_ai_ml_repo,
    SUM(fra.commits_count) AS total_commits_30d,
    SUM(fra.prs_merged) AS total_prs_merged_30d,
    SUM(fra.issues_closed) AS total_issues_closed_30d,
    SUM(fra.unique_contributors) AS total_unique_contributors_30d,
    SUM(fra.stars_gained) AS stars_gained_30d,
    MAX(fra.date_key) AS last_activity_date
FROM marts.dim_repository dr
LEFT JOIN marts.fct_repository_activity fra ON dr.repo_key = fra.repo_key
WHERE fra.date_key >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY dr.repo_id, dr.full_name, dr.primary_language, dr.is_ai_ml_repo;

-- Contributor Stats View
CREATE OR REPLACE VIEW analytics.contributor_stats AS
SELECT
    dc.contributor_id,
    dc.login,
    dc.name,
    dc.company,
    dc.location,
    dc.total_contributions,
    dc.total_repos_contributed,
    dc.first_contribution_date,
    dc.last_contribution_date,
    COUNT(DISTINCT fca.repo_key) AS active_repos_30d,
    SUM(fca.commits_count) AS commits_30d,
    SUM(fca.prs_merged) AS prs_merged_30d
FROM marts.dim_contributor dc
LEFT JOIN marts.fct_contributor_activity fca ON dc.contributor_key = fca.contributor_key
    AND fca.date_key >= CURRENT_DATE - INTERVAL '30 days'
WHERE dc.is_bot = FALSE
GROUP BY dc.contributor_key, dc.contributor_id, dc.login, dc.name, dc.company, dc.location,
         dc.total_contributions, dc.total_repos_contributed, dc.first_contribution_date, dc.last_contribution_date;

-- ============================================
-- POPULATE DIM_DATE
-- ============================================

INSERT INTO marts.dim_date (
    date_key, year, quarter, month, month_name, week, day_of_year,
    day_of_month, day_of_week, day_name, is_weekend
)
SELECT
    d::date,
    EXTRACT(YEAR FROM d)::int,
    EXTRACT(QUARTER FROM d)::int,
    EXTRACT(MONTH FROM d)::int,
    TO_CHAR(d, 'Month'),
    EXTRACT(WEEK FROM d)::int,
    EXTRACT(DOY FROM d)::int,
    EXTRACT(DAY FROM d)::int,
    EXTRACT(DOW FROM d)::int,
    TO_CHAR(d, 'Day'),
    EXTRACT(DOW FROM d) IN (0, 6)
FROM generate_series(
    '2020-01-01'::date,
    (CURRENT_DATE + INTERVAL '1 year')::date,
    '1 day'::interval
) d
ON CONFLICT (date_key) DO NOTHING;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT USAGE ON SCHEMA raw TO analytics;
GRANT USAGE ON SCHEMA staging TO analytics;
GRANT USAGE ON SCHEMA marts TO analytics;
GRANT USAGE ON SCHEMA analytics TO analytics;

GRANT SELECT ON ALL TABLES IN SCHEMA raw TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA staging TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics;

ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT SELECT ON TABLES TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT SELECT ON TABLES TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO analytics;