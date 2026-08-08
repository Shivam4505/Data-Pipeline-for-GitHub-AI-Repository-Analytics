-- GitHub AI Repository Analytics - Repository Daily Activity Fact
{{ config(materialized='table', unique_key='repo_key,date_key') }}

with daily as (
    select * from {{ ref('int_repo_activity_daily') }}
),

dim_repo as (
    select repo_key, repo_id from {{ ref('dim_repository') }}
),

dim_date as (
    select date_key from {{ ref('dim_date') }}
),

final as (
    select
        dr.repo_key,
        d.activity_date as date_key,
        d.commits_count,
        d.additions,
        d.deletions,
        d.files_changed,
        d.unique_contributors,
        d.issues_opened,
        d.issues_closed,
        d.prs_opened,
        d.prs_closed,
        d.prs_merged,
        d.releases_published,
        d.stars_gained,
        d.forks_gained,
        d.watchers_gained,
        current_timestamp as dbt_updated_at
    from daily d
    join dim_repo dr on d.repo_id = dr.repo_id
    join dim_date dd on d.activity_date = dd.date_key
)

select * from final