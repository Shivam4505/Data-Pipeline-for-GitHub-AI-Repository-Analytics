-- GitHub AI Repository Analytics - Contributor Dimension
{{ config(materialized='table', unique_key='contributor_id') }}

with stg as (
    select * from {{ ref('stg_contributors') }}
),

aggregated as (
    select
        contributor_id,
        max(contributor_login) as login,
        max(contributor_name) as name,
        max(contributor_email) as email,
        max(contributor_company) as company,
        max(contributor_location) as location,
        max(contributor_bio) as bio,
        max(contributor_avatar_url) as avatar_url,
        max(contributor_html_url) as html_url,
        max(contributor_type) as type,
        max(is_bot) as is_bot,
        max(is_organization_member) as is_organization_member,
        sum(contributions_count) as total_contributions,
        count(distinct repo_id) as total_repos_contributed,
        min(first_contribution_date) as first_contribution_date,
        max(last_contribution_date) as last_contribution_date
    from stg
    group by contributor_id
)

select
    contributor_id,
    login,
    name,
    email,
    company,
    location,
    bio,
    avatar_url,
    html_url,
    type,
    is_bot,
    is_organization_member,
    total_contributions,
    total_repos_contributed,
    first_contribution_date,
    last_contribution_date,
    current_timestamp as dbt_updated_at
from aggregated