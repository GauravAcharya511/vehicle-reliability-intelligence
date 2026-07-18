/*
 * SQL for DATA_MODE=postgres — mapped to the Vehicle Field Reliability
 * gold/silver schema. Each query aliases real columns to the canonical keys
 * the React client reads:
 *
 *   summary            -> total_units, total_failures, fleet_mttf_miles,
 *                         active_hotspots, overall_30d_failures, trend_pct, as_of
 *   mttfByComponent    -> component, mttf_miles, failures, units
 *   rollingFailureRate -> date, roll_30d, roll_60d, roll_90d
 *   regional           -> region, ratio, vehicles, failures, hotspot
 *   failureModes       -> mode, severity, count
 */
module.exports = {
  summary: `
    WITH base AS (
      SELECT COUNT(*)::bigint AS total_failures,
             COUNT(DISTINCT vin)::bigint AS total_units
      FROM silver.stg_repair_records
    ),
    mttf AS (
      SELECT ROUND(SUM(mttf_miles * failure_count) / NULLIF(SUM(failure_count), 0))::bigint
             AS fleet_mttf_miles
      FROM gold.fct_component_mttf
    ),
    hot AS (
      SELECT COUNT(*)::int AS active_hotspots
      FROM (
        SELECT component, region
        FROM gold.fct_failure_clusters
        WHERE is_hotspot
        GROUP BY component, region
      ) z
    ),
    daily AS (
      SELECT repair_date, SUM(rolling_30d_failures)::bigint AS r30
      FROM gold.fct_failure_rate_rolling
      GROUP BY repair_date
    ),
    trend AS (
      SELECT
        (SELECT r30 FROM daily ORDER BY repair_date DESC LIMIT 1)            AS latest,
        (SELECT r30 FROM daily ORDER BY repair_date DESC OFFSET 30 LIMIT 1)  AS prior,
        (SELECT MAX(repair_date) FROM daily)                                 AS as_of
    )
    SELECT
      base.total_units,
      base.total_failures,
      mttf.fleet_mttf_miles,
      hot.active_hotspots,
      COALESCE(trend.latest, 0)::bigint AS overall_30d_failures,
      CASE WHEN trend.prior > 0
           THEN ROUND(((trend.latest - trend.prior)::numeric / trend.prior) * 100, 1)
           ELSE 0 END AS trend_pct,
      to_char(trend.as_of, 'YYYY-MM-DD') AS as_of
    FROM base, mttf, hot, trend;
  `,

  mttfByComponent: `
    SELECT
      component,
      ROUND(SUM(mttf_miles * failure_count) / NULLIF(SUM(failure_count), 0))::bigint
        AS mttf_miles,
      SUM(failure_count)::bigint             AS failures,
      SUM(unique_vehicles_affected)::bigint  AS units
    FROM gold.fct_component_mttf
    GROUP BY component
    ORDER BY mttf_miles ASC;
  `,

  rollingFailureRate: `
    SELECT
      to_char(repair_date, 'YYYY-MM-DD')  AS date,
      SUM(rolling_30d_failures)::bigint    AS roll_30d,
      SUM(rolling_60d_failures)::bigint    AS roll_60d,
      SUM(rolling_90d_failures)::bigint    AS roll_90d
    FROM gold.fct_failure_rate_rolling
    GROUP BY repair_date
    ORDER BY repair_date ASC;
  `,

  // Component x region grain: averaging to region level washes out the signal
  // (one hot component per region + ten normal ones -> ~1.0). The real hotspots
  // live at the component-region pair level, so surface those directly.
  regional: `
    SELECT
      component,
      region,
      ROUND(AVG(regional_vs_baseline_ratio)::numeric, 2) AS ratio,
      SUM(regional_failure_count)::bigint                AS failures,
      (AVG(regional_vs_baseline_ratio) >= 1.4)           AS hotspot
    FROM gold.fct_failure_clusters
    GROUP BY component, region
    ORDER BY ratio DESC
    LIMIT 8;
  `,

  failureModes: `
    SELECT
      nlp_failure_category                                   AS mode,
      LOWER(mode() WITHIN GROUP (ORDER BY nlp_severity))     AS severity,
      COUNT(*)::bigint                                       AS count
    FROM gold.fct_repair_nlp_enriched
    WHERE nlp_failure_category IS NOT NULL
    GROUP BY nlp_failure_category
    ORDER BY count DESC
    LIMIT 10;
  `,
};
