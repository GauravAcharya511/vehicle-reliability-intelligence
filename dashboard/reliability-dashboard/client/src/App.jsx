import { useEffect, useState } from "react";
import { api } from "./api.js";
import MttfByComponent from "./components/MttfByComponent.jsx";
import RollingFailureRate from "./components/RollingFailureRate.jsx";
import RegionalFailure from "./components/RegionalFailure.jsx";
import FailureModes from "./components/FailureModes.jsx";

function Kpi({ label, value, unit, delta }) {
  return (
    <div className="kpi">
      <div className="label">{label}</div>
      <div className="value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {delta != null && (
        <div className={`delta ${delta >= 0 ? "up" : "down"}`}>
          {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}% vs prior 30d
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.summary(), api.mttfByComponent(), api.rollingFailureRate(),
      api.regional(), api.failureModes(),
    ])
      .then(([summary, mttf, rolling, regional, modes]) =>
        setData({ summary, mttf, rolling, regional, modes })
      )
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="state">
        <div className="err">
          Could not reach the reliability API.<br />{error}<br /><br />
          Start it with <code>npm run dev</code> from the project root.
        </div>
      </div>
    );
  }
  if (!data) return <div className="state">Initializing telemetry…</div>;

  const s = data.summary;
  const n = (v) => Number(v).toLocaleString();

  return (
    <div className="app">
      <header className="masthead">
        <div>
          <h1><span className="pulse" />Fleet Reliability Console</h1>
          <div className="sub">PROGNOSTICS &amp; HEALTH MANAGEMENT · VEHICLE FIELD DATA</div>
        </div>
        <div className="asof">
          <div>AS OF {s.as_of}</div>
          <div>SOURCE <span className="mode">pipeline gold layer</span></div>
        </div>
      </header>

      <section className="kpi-strip">
        <Kpi label="Units in field" value={n(s.total_units)} />
        <Kpi label="Total failures" value={n(s.total_failures)} />
        <Kpi label="Fleet MTTF" value={n(s.fleet_mttf_miles)} unit="mi" />
        <Kpi label="30-day failures" value={n(s.overall_30d_failures)} delta={s.trend_pct} />
        <Kpi label="Active hotspots" value={s.active_hotspots} />
      </section>

      <RollingFailureRate data={data.rolling} />
      <div className="grid" style={{ marginTop: 16 }}>
        <MttfByComponent data={data.mttf} />
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <RegionalFailure data={data.regional} />
          <FailureModes data={data.modes} />
        </div>
      </div>
    </div>
  );
}
