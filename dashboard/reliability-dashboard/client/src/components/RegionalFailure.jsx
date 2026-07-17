export default function RegionalFailure({ data }) {
  const maxRatio = Math.max(...data.map((d) => d.ratio));
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Regional Clustering</h2>
        <span className="hint">rate vs. fleet baseline</span>
      </div>
      <p className="panel-desc">
        Regions above 1.4&times; baseline are flagged as hotspots for investigation.
      </p>
      <table className="reg-table">
        <thead>
          <tr>
            <th>Region</th>
            <th style={{ width: "36%" }}>Ratio to baseline</th>
            <th className="num">Vehicles</th>
            <th className="num">Failures</th>
          </tr>
        </thead>
        <tbody>
          {data.map((r) => (
            <tr key={r.region}>
              <td>{r.region} {r.hotspot && <span className="badge">hotspot</span>}</td>
              <td>
                <span className="ratio-bar">
                  <span className="ratio-track">
                    <span className="ratio-fill" style={{
                      width: `${(r.ratio / maxRatio) * 100}%`,
                      background: r.hotspot ? "var(--crit)" : "var(--accent)",
                    }} />
                  </span>
                  <span style={{ fontFamily: "var(--mono)", fontSize: 11 }}>
                    {Number(r.ratio).toFixed(2)}&times;
                  </span>
                </span>
              </td>
              <td className="num">{Number(r.vehicles).toLocaleString()}</td>
              <td className="num">{Number(r.failures).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
