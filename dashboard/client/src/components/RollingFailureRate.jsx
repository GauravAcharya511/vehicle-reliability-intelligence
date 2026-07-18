import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip,
} from "recharts";
import ConsoleTooltip from "./Tooltip.jsx";

export default function RollingFailureRate({ data }) {
  const ticks = data.filter((_, i) => i % 15 === 0).map((d) => d.date);
  return (
    <section className="panel wide">
      <div className="panel-head">
        <h2>Rolling Failure Volume</h2>
        <span className="hint">failures in trailing window</span>
      </div>
      <p className="panel-desc">
        Failure counts over trailing 30 / 60 / 90-day windows. A rising 30-day line
        relative to the longer windows signals accelerating failures.
      </p>
      <div className="legend">
        <span><i className="swatch" style={{ background: "var(--accent)" }} /> 30-day</span>
        <span><i className="swatch" style={{ background: "var(--warn)" }} /> 60-day</span>
        <span><i className="swatch" style={{ background: "var(--text-faint)" }} /> 90-day</span>
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: -8, bottom: 0 }}>
          <CartesianGrid stroke="var(--line-soft)" />
          <XAxis
            dataKey="date" ticks={ticks} stroke="var(--text-faint)"
            tick={{ fontSize: 10, fontFamily: "var(--mono)" }} tickFormatter={(d) => d.slice(5)}
          />
          <YAxis stroke="var(--text-faint)" tick={{ fontSize: 10, fontFamily: "var(--mono)" }} />
          <Tooltip content={<ConsoleTooltip />} />
          <Line type="monotone" dataKey="roll_90d" name="90-day" stroke="var(--text-faint)" strokeWidth={1.5} dot={false} />
          <Line type="monotone" dataKey="roll_60d" name="60-day" stroke="var(--warn)" strokeWidth={1.5} dot={false} />
          <Line type="monotone" dataKey="roll_30d" name="30-day" stroke="var(--accent)" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
