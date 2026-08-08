-- GitHub AI Repository Analytics - Repository Dimension
{{ config(materialized='table', unique_key='repo_id') }}

with stg as (
    select * from {{ ref('stg_repositories') }}
),

health as (
    select * from {{ ref('fct_repository_health') }}
),

final as (
    select
        s.repo_id,
        s.node_id,
        s.name,
        s.full_name,
        s.owner_login,
        s.owner_type,
        s.description,
        s.homepage,
        s.html_url,
        s.language as primary_language,
        s.languages,
        s.topics,
        s.ai_ml_topics,
        s.is_ai_ml_repo,
        s.license_key,
        s.license_name,
        s.is_fork,
        s.is_archived,
        s.default_branch,
        s.created_at,
        s.updated_at,
        s.pushed_at,
        s.size_kb,
        s.stargazers_count,
        s.watchers_count,
        s.forks_count,
        s.open_issues_count,
        s.subscribers_count,
        s.network_count,
        s.contributors_count,
        s.releases_count,
        s.commits_count,
        h.health_score,
        case
            when h.health_score >= 80 then 'A'
            when h.health_score >= 60 then 'B'
            when h.health_score >= 40 then 'C'
            when h.health_score >= 20 then 'D'
            else 'F'
        end as health_grade,
        case
            when s.created_at > current_date - interval '6 months' then 'New'
            when s.created_at > current_date - interval '2 years' then 'Growing'
            when s.created_at > current_date - interval '5 years' then 'Mature'
            else 'Established'
        end as maturity_level,
        current_timestamp as dbt_updated_at
    from stg s
    left join health h on s.repo_id = h.repo_key
)

select * from final