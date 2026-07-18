export default function RegionalFailure({ data }) {
  const maxRatio = Math.max(...data.map((d) => d.ratio));
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Regional Hotspots</h2>
        <span className="hint">component × region vs. baseline</span>
      </div>
      <p className="panel-desc">
        Component-region pairs failing above 1.4&times; the fleet baseline, ranked
        by severity. These are the clusters worth investigating.
      </p>
      <table className="reg-table">
        <thead>
          <tr>
            <th>Component / Region</th>
            <th style={{ width: "34%" }}>Ratio to baseline</th>
            <th className="num">Failures</th>
          </tr>
        </thead>
        <tbody>
          {data.map((r) => (
            <tr key={`${r.component}-${r.region}`}>
              <td>
                <span style={{ display: "block", fontSize: 12.5 }}>{r.component}</span>
                <span style={{ fontSize: 11, color: "var(--text-dim)" }}>
                  {r.region} {r.hotspot && <span className="badge">hotspot</span>}
                </span>
              </td>
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
              <td className="num">{Number(r.failures).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
