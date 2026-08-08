-- GitHub AI Repository Analytics - Staging Contributors
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'contributors') }}
),

cleaned as (
    select
        id,
        repo_id,
        contributor_id,
        contributor_login,
        contributor_name,
        contributor_email,
        contributor_company,
        contributor_location,
        contributor_bio,
        contributor_avatar_url,
        contributor_html_url,
        contributor_type,
        contributions_count,
        additions,
        deletions,
        commit_count,
        first_contribution_date,
        last_contribution_date,
        is_organization_member,
        -- Bot detection
        contributor_login ILIKE '%bot%' 
        or contributor_login ILIKE '%[bot]%' 
        or contributor_type = 'Bot' as is_bot,
        collected_at
    from source
)

select * from cleaned