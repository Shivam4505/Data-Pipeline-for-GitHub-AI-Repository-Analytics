-- GitHub AI Repository Analytics - Staging Pull Requests
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'pull_requests') }}
),

cleaned as (
    select
        id,
        repo_id,
        pr_id,
        number,
        title,
        body,
        state,
        draft,
        author_id,
        author_login,
        author_type,
        assignee_login,
        labels,
        milestone_title,
        base_ref,
        base_sha,
        head_ref,
        head_sha,
        head_repo_id,
        head_repo_full_name,
        comments_count,
        review_comments_count,
        commits_count,
        additions,
        deletions,
        changed_files,
        mergeable,
        mergeable_state,
        merged,
        merged_at,
        merged_by_login,
        closed_at,
        -- Bot detection
        author_login ILIKE '%bot%' 
        or author_login ILIKE '%[bot]%' as is_bot_pr,
        -- Time to merge in hours
        case 
            when merged_at is not null 
            then extract(epoch from (merged_at - created_at)) / 3600 
        end as time_to_merge_hours,
        created_at::date as created_date,
        merged_at::date as merged_date,
        created_at,
        updated_at,
        collected_at
    from source
)

select * from cleaned