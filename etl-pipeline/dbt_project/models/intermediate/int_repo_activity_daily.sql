-- GitHub AI Repository Analytics - Intermediate Daily Repository Activity
{{ config(materialized='view') }}

with commits as (
    select
        repo_id,
        commit_date as activity_date,
        count(*) as commits_count,
        sum(additions) as additions,
        sum(deletions) as deletions,
        sum(files_changed) as files_changed,
        count(distinct author_login) as unique_contributors
    from {{ ref('stg_commits') }}
    where not is_bot_commit
    group by repo_id, commit_date
),

issues as (
    select
        repo_id,
        created_date as activity_date,
        count(*) filter (where state = 'open') as issues_opened,
        count(*) filter (where state = 'closed') as issues_closed
    from {{ ref('stg_issues') }}
    where not is_bot_issue
    group by repo_id, created_date
),

issues_closed as (
    select
        repo_id,
        closed_date as activity_date,
        count(*) as issues_closed
    from {{ ref('stg_issues') }}
    where not is_bot_issue and closed_date is not null
    group by repo_id, closed_date
),

prs as (
    select
        repo_id,
        created_date as activity_date,
        count(*) filter (where state = 'open') as prs_opened,
        count(*) filter (where state = 'closed') as prs_closed,
        count(*) filter (where merged = true) as prs_merged
    from {{ ref('stg_pull_requests') }}
    where not is_bot_pr
    group by repo_id, created_date
),

prs_merged as (
    select
        repo_id,
        merged_date as activity_date,
        count(*) as prs_merged
    from {{ ref('stg_pull_requests') }}
    where not is_bot_pr and merged_date is not null
    group by repo_id, merged_date
),

releases as (
    select
        repo_id,
        published_at::date as activity_date,
        count(*) as releases_published
    from {{ source('raw', 'releases') }}
    where published_at is not null
    group by repo_id, published_at::date
),

stargazers as (
    select
        repo_id,
        starred_at::date as activity_date,
        count(*) as stars_gained
    from {{ source('raw', 'stargazers') }}
    group by repo_id, starred_at::date
),

all_dates as (
    select repo_id, activity_date from commits
    union
    select repo_id, activity_date from issues
    union
    select repo_id, activity_date from issues_closed
    union
    select repo_id, activity_date from prs
    union
    select repo_id, activity_date from prs_merged
    union
    select repo_id, activity_date from releases
    union
    select repo_id, activity_date from stargazers
),

combined as (
    select
        ad.repo_id,
        ad.activity_date,
        coalesce(c.commits_count, 0) as commits_count,
        coalesce(c.additions, 0) as additions,
        coalesce(c.deletions, 0) as deletions,
        coalesce(c.files_changed, 0) as files_changed,
        coalesce(c.unique_contributors, 0) as unique_contributors,
        coalesce(i.issues_opened, 0) as issues_opened,
        coalesce(ic.issues_closed, 0) as issues_closed,
        coalesce(p.prs_opened, 0) as prs_opened,
        coalesce(p.prs_closed, 0) as prs_closed,
        coalesce(pm.prs_merged, 0) as prs_merged,
        coalesce(r.releases_published, 0) as releases_published,
        coalesce(s.stars_gained, 0) as stars_gained,
        0 as forks_gained,  -- Would need fork events
        0 as watchers_gained  -- Would need watcher events
    from all_dates ad
    left join commits c on ad.repo_id = c.repo_id and ad.activity_date = c.activity_date
    left join issues i on ad.repo_id = i.repo_id and ad.activity_date = i.activity_date
    left join issues_closed ic on ad.repo_id = ic.repo_id and ad.activity_date = ic.activity_date
    left join prs p on ad.repo_id = p.repo_id and ad.activity_date = p.activity_date
    left join prs_merged pm on ad.repo_id = pm.repo_id and ad.activity_date = pm.activity_date
    left join releases r on ad.repo_id = r.repo_id and ad.activity_date = r.activity_date
    left join stargazers s on ad.repo_id = s.repo_id and ad.activity_date = s.activity_date
)

select * from combined