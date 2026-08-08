-- GitHub AI Repository Analytics - Staging Issues
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'issues') }}
),

cleaned as (
    select
        id,
        repo_id,
        issue_id,
        number,
        title,
        body,
        state,
        state_reason,
        author_id,
        author_login,
        author_type,
        assignee_login,
        labels,
        milestone_title,
        milestone_state,
        comments_count,
        (reactions->>'total_count')::int as reactions_total,
        is_pull_request,
        -- Bot detection
        author_login ILIKE '%bot%' 
        or author_login ILIKE '%[bot]%' as is_bot_issue,
        created_at,
        updated_at,
        closed_at,
        -- Resolution time in hours
        case 
            when closed_at is not null 
            then extract(epoch from (closed_at - created_at)) / 3600 
        end as resolution_time_hours,
        created_at::date as created_date,
        closed_at::date as closed_date,
        collected_at
    from source
)

select * from cleaned