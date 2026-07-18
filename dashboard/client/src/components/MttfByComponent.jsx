import {
  BarChart, Bar, XAxis, YAxis, Cell, ResponsiveContainer, Tooltip, CartesianGrid,
} from "recharts";
import ConsoleTooltip from "./Tooltip.jsx";

// Color by rank so it adapts to any MTTF scale: worst quartile critical, best ok.
function bandColor(index, total) {
  const q = index / total;
  if (q < 0.25) return "var(--crit)";
  if (q < 0.5) return "var(--high)";
  if (q < 0.75) return "var(--warn)";
  return "var(--ok)";
}

export default function MttfByComponent({ data }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Mean Time To Failure</h2>
        <span className="hint">miles · by component</span>
      </div>
      <p className="panel-desc">
        Lowest-MTTF components carry the highest field risk. Sorted worst-first.
      </p>
      <ResponsiveContainer width="100%" height={data.length * 30 + 20}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 24, left: 8, bottom: 0 }}>
          <CartesianGrid horizontal={false} stroke="var(--line-soft)" />
          <XAxis
            type="number" stroke="var(--text-faint)"
            tick={{ fontSize: 10, fontFamily: "var(--mono)" }}
            tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
          />
          <YAxis
            type="category" dataKey="component" width={130}
            stroke="var(--text-faint)" tick={{ fontSize: 11, fill: "var(--text-dim)" }}
          />
          <Tooltip cursor={{ fill: "rgba(255,255,255,0.03)" }} content={<ConsoleTooltip unit=" mi" />} />
          <Bar dataKey="mttf_miles" name="MTTF" barSize={13}>
            {data.map((d, i) => (
              <Cell key={d.component} fill={bandColor(i, data.length)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
