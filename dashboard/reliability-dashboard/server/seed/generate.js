/*
 * Seed generator — placeholder dataset shaped like the gold-layer output of the
 * Vehicle Field Reliability pipeline, using the SAME canonical keys the Postgres
 * queries return, so the UI is identical in both modes. Replace by setting
 * DATA_MODE=postgres.
 */
const fs = require("fs");
const path = require("path");

function rng(seed) {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}
const rand = rng(42);
const round = (n, d = 1) => Number(n.toFixed(d));

const COMPONENTS = [
  "Battery Pack", "Drive Unit", "Power Electronics", "Charging Port",
  "Thermal Management", "Brakes", "Suspension", "HVAC System",
  "Autopilot Sensors", "Body & Trim",
];
const REGIONS = ["West", "Southwest", "Midwest", "Northeast", "Southeast", "Pacific NW"];
const MODES = [
  { mode: "Thermal derating", severity: "critical" },
  { mode: "Insulation breakdown", severity: "critical" },
  { mode: "Coolant flow fault", severity: "high" },
  { mode: "Sensor calibration drift", severity: "high" },
  { mode: "Connector wear", severity: "medium" },
  { mode: "Firmware fault", severity: "medium" },
  { mode: "Seal degradation", severity: "low" },
  { mode: "Cosmetic wear", severity: "low" },
];

// MTTF in miles per component (lower = worse).
const mttfByComponent = COMPONENTS.map((component) => {
  const units = 800 + Math.floor(rand() * 4200);
  const mttf_miles = Math.round(18000 + rand() * 120000);
  const failures = Math.max(5, Math.round(units * (40000 / mttf_miles) / 6));
  return { component, mttf_miles, failures, units };
}).sort((a, b) => a.mttf_miles - b.mttf_miles);

// Rolling failure COUNTS over 30/60/90-day trailing windows.
const rollingFailureRate = [];
const start = new Date("2026-04-15T00:00:00Z");
let daily = 14;
const dailies = [];
for (let i = 0; i < 120; i++) {
  daily += (rand() - 0.48) * 2;
  daily = Math.max(4, daily);
  dailies.push(daily);
}
for (let i = 29; i < 120; i++) {
  const d = new Date(start.getTime() + i * 86400000);
  const sum = (n) =>
    Math.round(dailies.slice(Math.max(0, i - n + 1), i + 1).reduce((a, b) => a + b, 0));
  rollingFailureRate.push({
    date: d.toISOString().slice(0, 10),
    roll_30d: sum(30),
    roll_60d: sum(60),
    roll_90d: sum(90),
  });
}

// Regional clustering.
const regional = REGIONS.map((region) => {
  const ratio = round(0.6 + rand() * 1.9, 2);
  return {
    region,
    ratio,
    vehicles: Math.round(300 + rand() * 1400),
    failures: Math.round(ratio * (120 + rand() * 260)),
    hotspot: ratio >= 1.4,
  };
}).sort((a, b) => b.ratio - a.ratio);

const failureModes = MODES.map((m) => ({
  ...m,
  count: 40 + Math.floor(rand() * 320),
})).sort((a, b) => b.count - a.count);

const total_units = mttfByComponent.reduce((s, c) => s + c.units, 0);
const total_failures = mttfByComponent.reduce((s, c) => s + c.failures, 0);
const fleet_mttf_miles = Math.round(
  mttfByComponent.reduce((s, c) => s + c.mttf_miles * c.failures, 0) /
    mttfByComponent.reduce((s, c) => s + c.failures, 0)
);
const last = rollingFailureRate[rollingFailureRate.length - 1];
const prev = rollingFailureRate[rollingFailureRate.length - 31];
const trend_pct = round(((last.roll_30d - prev.roll_30d) / prev.roll_30d) * 100);

const summary = {
  total_units,
  total_failures,
  fleet_mttf_miles,
  active_hotspots: regional.filter((r) => r.hotspot).length,
  overall_30d_failures: last.roll_30d,
  trend_pct,
  as_of: last.date,
};

const data = { summary, mttfByComponent, rollingFailureRate, regional, failureModes };
fs.writeFileSync(path.join(__dirname, "data.json"), JSON.stringify(data, null, 2));
console.log(
  `Seed written · ${total_units.toLocaleString()} units · ${total_failures.toLocaleString()} failures · ` +
    `fleet MTTF ${fleet_mttf_miles.toLocaleString()} mi · ${summary.active_hotspots} hotspots`
);
