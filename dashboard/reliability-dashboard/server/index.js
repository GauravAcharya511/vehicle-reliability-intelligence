require("dotenv").config();
const express = require("express");
const cors = require("cors");
const db = require("./db");

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());

// Wrap each handler so a data-layer error returns a clean 500 with a message,
// instead of hanging the request.
function handler(fn) {
  return async (req, res) => {
    try {
      res.json(await fn());
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message });
    }
  };
}

app.get("/api/health", (req, res) => res.json({ ok: true, mode: db.mode }));
app.get("/api/summary", handler(db.summary));
app.get("/api/mttf-by-component", handler(db.mttfByComponent));
app.get("/api/rolling-failure-rate", handler(db.rollingFailureRate));
app.get("/api/regional", handler(db.regional));
app.get("/api/failure-modes", handler(db.failureModes));

app.listen(PORT, () => {
  console.log(`Reliability API running on :${PORT} (data mode: ${db.mode})`);
});
