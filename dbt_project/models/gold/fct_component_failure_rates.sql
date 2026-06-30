{{
    config(
        materialized='table',
        schema='gold',
        description='Monthly component failure rates by region and mileage band'
    )
}}

SELECT
    component,
    region,
    continent,
    repair_month,
    repair_year,
    mileage_band,
    COUNT(*) AS total_repairs,
    COUNT(DISTINCT vin) AS unique_vehicles,
    AVG(repair_cost_usd) AS avg_repair_cost_usd,
    SUM(repair_cost_usd) AS total_repair_cost_usd,
    SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) AS warranty_claims,
    ROUND(
        100.0 * SUM(CASE WHEN warranty_claim THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS warranty_claim_rate_pct,
    AVG(vehicle_age_at_repair) AS avg_vehicle_age_at_repair,
    SUM(CASE WHEN cost_severity = 'Critical' THEN 1 ELSE 0 END) AS critical_repairs
FROM {{ ref('stg_repair_records') }}
GROUP BY component, region, continent, repair_month, repair_year, mileage_band
ORDER BY repair_month DESC, total_repairs DESC
