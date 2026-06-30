-- =============================================================================
-- Vehicle Field Reliability Intelligence System
-- Medallion architecture schema (Bronze / Silver / Gold)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

COMMENT ON SCHEMA bronze IS 'Raw ingested data, immutable source of truth';
COMMENT ON SCHEMA silver IS 'Cleaned, validated, deduplicated data';
COMMENT ON SCHEMA gold IS 'Business-ready aggregates and KPIs';

-- =============================================================================
-- BRONZE LAYER: Raw repair records
-- =============================================================================

CREATE TABLE IF NOT EXISTS bronze.repair_records_raw (
    record_id           BIGSERIAL PRIMARY KEY,
    vin                 VARCHAR(17)   NOT NULL,
    repair_date         DATE          NOT NULL,
    component           VARCHAR(100)  NOT NULL,
    failure_mode        VARCHAR(200),
    repair_description  TEXT,
    mileage             INTEGER,
    repair_cost_usd     NUMERIC(10,2),
    region              VARCHAR(50),
    dealer_id           VARCHAR(20),
    vehicle_model       VARCHAR(50),
    vehicle_year        INTEGER,
    warranty_claim      BOOLEAN,

    -- Audit columns (mandatory in production)
    source_system       VARCHAR(50)   NOT NULL DEFAULT 'simulated_fleet_v1',
    ingested_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    record_hash         VARCHAR(64),

    CONSTRAINT chk_vin_length CHECK (LENGTH(vin) = 17),
    CONSTRAINT chk_mileage_positive CHECK (mileage IS NULL OR mileage >= 0),
    CONSTRAINT chk_cost_positive CHECK (repair_cost_usd IS NULL OR repair_cost_usd >= 0),
    CONSTRAINT chk_vehicle_year_range CHECK (vehicle_year IS NULL OR vehicle_year BETWEEN 2010 AND 2030)
);

-- Indexes optimized for analytical query patterns
CREATE INDEX IF NOT EXISTS idx_repair_vin           ON bronze.repair_records_raw(vin);
CREATE INDEX IF NOT EXISTS idx_repair_date          ON bronze.repair_records_raw(repair_date);
CREATE INDEX IF NOT EXISTS idx_repair_component     ON bronze.repair_records_raw(component);
CREATE INDEX IF NOT EXISTS idx_repair_region        ON bronze.repair_records_raw(region);
CREATE INDEX IF NOT EXISTS idx_repair_component_dt  ON bronze.repair_records_raw(component, repair_date);
CREATE INDEX IF NOT EXISTS idx_repair_ingested_at   ON bronze.repair_records_raw(ingested_at);

COMMENT ON TABLE bronze.repair_records_raw IS
'Raw repair records as received from fleet data sources. Immutable. Source of truth for all downstream layers.';

COMMENT ON COLUMN bronze.repair_records_raw.record_hash IS
'SHA-256 hash of source row used for idempotent ingestion and deduplication';

-- =============================================================================
-- METADATA: Pipeline run tracking
-- =============================================================================

CREATE TABLE IF NOT EXISTS bronze.pipeline_runs (
    run_id              BIGSERIAL PRIMARY KEY,
    pipeline_name       VARCHAR(100)  NOT NULL,
    status              VARCHAR(20)   NOT NULL,
    started_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    records_processed   INTEGER,
    records_failed      INTEGER       DEFAULT 0,
    error_message       TEXT,

    CONSTRAINT chk_status CHECK (status IN ('STARTED', 'SUCCESS', 'FAILED', 'PARTIAL'))
);

CREATE INDEX IF NOT EXISTS idx_pipeline_name_started ON bronze.pipeline_runs(pipeline_name, started_at DESC);

COMMENT ON TABLE bronze.pipeline_runs IS
'Tracks every pipeline execution for observability, debugging, and SLA monitoring';
