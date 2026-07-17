const SEV_COLOR = {
  critical: "var(--crit)",
  high: "var(--high)",
  medium: "var(--warn)",
  moderate: "var(--warn)",
  low: "var(--text-dim)",
  minor: "var(--text-dim)",
};
// Fallback for any severity label the NLP layer emits that we haven't styled.
const colorFor = (sev) => SEV_COLOR[(sev || "").toLowerCase()] || "var(--text-dim)";
const classFor = (sev) => {
  const s = (sev || "").toLowerCase();
  return ["critical", "high", "medium", "low"].includes(s) ? s : "medium";
};

export default function FailureModes({ data }) {
  const max = Math.max(...data.map((d) => d.count));
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Top Failure Modes</h2>
        <span className="hint">classified from repair text</span>
      </div>
      <p className="panel-desc">
        Free-text repair descriptions categorized by failure type and severity.
      </p>
      <div>
        {data.map((m) => (
          <div className="mode-row" key={m.mode}>
            <span className={`sev-dot sev-${classFor(m.severity)}`} title={m.severity} />
            <div>
              <div className="mode-name">{m.mode}</div>
              <div className="mode-meter">
                <span style={{ width: `${(m.count / max) * 100}%`, background: colorFor(m.severity) }} />
              </div>
            </div>
            <span className="mode-count">{Number(m.count).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
