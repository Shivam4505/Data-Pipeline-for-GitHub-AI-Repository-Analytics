-- GitHub AI Repository Analytics - Staging Repositories
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'repositories') }}
),

cleaned as (
    select
        id as repo_id,
        node_id,
        name,
        full_name,
        owner_login,
        owner_type,
        owner_id,
        description,
        homepage,
        html_url,
        language,
        languages_json as languages,
        topics,
        default_branch,
        license_key,
        license_name,
        license_spdx_id,
        is_private,
        is_fork,
        is_archived,
        is_template,
        has_issues,
        has_projects,
        has_wiki,
        has_pages,
        has_discussions,
        pushed_at,
        created_at,
        updated_at,
        size_kb,
        stargazers_count,
        watchers_count,
        forks_count,
        open_issues_count,
        subscribers_count,
        network_count,
        contributors_count,
        releases_count,
        commits_count,
        -- AI/ML classification
        topics && var('ai_ml_topics') as is_ai_ml_repo,
        topics & var('ai_ml_topics') as ai_ml_topics,
        collected_at
    from source
)

select * from cleaned