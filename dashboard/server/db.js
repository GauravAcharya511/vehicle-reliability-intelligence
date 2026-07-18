/*
 * Data access layer.
 *
 * DATA_MODE=seed      -> serves server/seed/data.json (default; runs with zero setup)
 * DATA_MODE=postgres  -> queries the real Vehicle Field Reliability gold tables
 *
 * To go live: set DATA_MODE=postgres and DATABASE_URL in .env, then map the SQL
 * in queries.js to your actual table / column names.
 */
const fs = require("fs");
const path = require("path");
const Q = require("./queries");

const MODE = process.env.DATA_MODE || "seed";

let pool = null;
if (MODE === "postgres") {
  const { Pool } = require("pg");
  pool = new Pool({ connectionString: process.env.DATABASE_URL });
}

function loadSeed() {
  const p = path.join(__dirname, "seed", "data.json");
  if (!fs.existsSync(p)) {
    throw new Error("Seed data missing. Run: node server/seed/generate.js");
  }
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

async function rows(sql) {
  const res = await pool.query(sql);
  return res.rows;
}

// Each getter returns the same shape whether it comes from seed or Postgres,
// so the API and the React client never need to know which mode is active.
const providers = {
  seed: {
    summary: async () => loadSeed().summary,
    mttfByComponent: async () => loadSeed().mttfByComponent,
    rollingFailureRate: async () => loadSeed().rollingFailureRate,
    regional: async () => loadSeed().regional,
    failureModes: async () => loadSeed().failureModes,
  },
  postgres: {
    summary: async () => (await rows(Q.summary))[0],
    mttfByComponent: async () => rows(Q.mttfByComponent),
    rollingFailureRate: async () => rows(Q.rollingFailureRate),
    regional: async () => rows(Q.regional),
    failureModes: async () => rows(Q.failureModes),
  },
};

module.exports = { mode: MODE, ...providers[MODE] };
