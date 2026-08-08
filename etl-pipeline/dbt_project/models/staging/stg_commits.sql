-- GitHub AI Repository Analytics - Staging Commits
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'commits') }}
),

cleaned as (
    select
        id,
        repo_id,
        sha,
        node_id,
        author_id,
        author_login,
        author_name,
        author_email,
        author_date,
        committer_date,
        message,
        split_part(message, E'\n', 1) as message_headline,
        additions,
        deletions,
        total_changes,
        files_changed,
        parents_sha,
        is_merge,
        -- Bot detection
        author_login ILIKE '%bot%' 
        or author_login ILIKE '%[bot]%' 
        or author_email ILIKE '%bot%' as is_bot_commit,
        -- Date dimensions
        author_date::date as commit_date,
        date_trunc('week', author_date)::date as commit_week,
        date_trunc('month', author_date)::date as commit_month,
        collected_at
    from source
)

select * from cleaned