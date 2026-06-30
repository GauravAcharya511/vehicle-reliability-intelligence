{{
    config(
        materialized='table',
        schema='gold',
        description='Top failure modes ranked by frequency and cost impact'
    )
}}

SELECT
    component,
    failure_mode,
    COUNT(*) AS occurrence_count,
    COUNT(DISTINCT vin) AS affected_vehicles,
    AVG(repair_cost_usd) AS avg_cost_per_occurrence,
    SUM(repair_cost_usd) AS total_cost_impact,
    AVG(mileage) AS avg_mileage_at_failure,
    AVG(vehicle_age_at_repair) AS avg_vehicle_age_at_failure,
    ROUND(
        100.0 * SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS warranty_claim_rate_pct
FROM {{ ref('stg_repair_records') }}
GROUP BY component, failure_mode
ORDER BY total_cost_impact DESC
