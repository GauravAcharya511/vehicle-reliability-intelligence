// Thin fetch wrapper. Paths are proxied to the Express API by Vite (see vite.config.js).
async function get(path) {
  const res = await fetch(path);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  summary: () => get("/api/summary"),
  mttfByComponent: () => get("/api/mttf-by-component"),
  rollingFailureRate: () => get("/api/rolling-failure-rate"),
  regional: () => get("/api/regional"),
  failureModes: () => get("/api/failure-modes"),
};
