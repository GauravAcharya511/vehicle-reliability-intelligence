{{
    config(
        materialized='view',
        schema='silver',
        description='Cleaned and enriched repair records with derived dimensions'
    )
}}

WITH source AS (
    SELECT *
    FROM {{ source('bronze', 'repair_records_raw') }}
),

cleaned AS (
    SELECT
        record_id,
        vin,
        repair_date,
        DATE_TRUNC('month', repair_date)::date AS repair_month,
        DATE_TRUNC('quarter', repair_date)::date AS repair_quarter,
        EXTRACT(YEAR FROM repair_date)::int AS repair_year,
        component,
        failure_mode,
        repair_description,
        mileage,
        repair_cost_usd,
        region,
        SPLIT_PART(region, '-', 1) AS continent,
        dealer_id,
        vehicle_model,
        vehicle_year,
        (EXTRACT(YEAR FROM repair_date)::int - vehicle_year) AS vehicle_age_at_repair,
        warranty_claim,
        CASE
            WHEN mileage < 20000 THEN 'Low (<20k)'
            WHEN mileage < 50000 THEN 'Mid (20-50k)'
            WHEN mileage < 100000 THEN 'High (50-100k)'
            ELSE 'Very High (100k+)'
        END AS mileage_band,
        CASE
            WHEN repair_cost_usd < 500 THEN 'Low'
            WHEN repair_cost_usd < 2000 THEN 'Medium'
            WHEN repair_cost_usd < 5000 THEN 'High'
            ELSE 'Critical'
        END AS cost_severity,
        source_system,
        ingested_at,
        record_hash
    FROM source
    WHERE repair_date IS NOT NULL
      AND vin IS NOT NULL
      AND component IS NOT NULL
)

SELECT * FROM cleaned
