/**
 * Vercel Serverless API Proxy for InnoStudio.
 * Forwards /api/* requests to https://power.renhesports.com/api/* with clean
 * Origin/Referer headers (matching nginx.conf), avoiding browser CORS blocks.
 * Local-only hardware/sync endpoints (/api/power/*, /api/opengym/*, /api/token)
 * return 404 JSON so the frontend hides those optional widgets cleanly.
 */

const UPSTREAM_ORIGIN = "https://power.renhesports.com";

async function readBody(req) {
  if (req.method === "GET" || req.method === "HEAD") return undefined;
  if (req.body !== undefined && req.body !== null) {
    if (Buffer.isBuffer(req.body)) return req.body;
    if (typeof req.body === "string") return req.body;
    return JSON.stringify(req.body);
  }
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return chunks.length ? Buffer.concat(chunks) : undefined;
}

module.exports = async function handler(req, res) {
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    return res.status(204).end();
  }

  const parsedUrl = new URL(req.url || "/api/", "https://localhost");
  const apiPath = parsedUrl.pathname.startsWith("/api/")
    ? parsedUrl.pathname
    : "/api/" + (Array.isArray(req.query?.path) ? req.query.path.join("/") : (req.query?.path || ""));

  if (
    apiPath.startsWith("/api/power/") ||
    apiPath.startsWith("/api/opengym/") ||
    apiPath === "/api/token"
  ) {
    return res.status(404).json({
      success: false,
      configured: false,
      error: "Local-only endpoint is not available in cloud deployment",
    });
  }

  const targetUrl = `${UPSTREAM_ORIGIN}${apiPath}${parsedUrl.search}`;
  const headers = {
    Host: "power.renhesports.com",
    Origin: UPSTREAM_ORIGIN,
    Referer: `${UPSTREAM_ORIGIN}/`,
    Accept: "application/json, text/plain, */*",
    "User-Agent": req.headers["user-agent"] || "InnoStudio-Vercel-Proxy/1.0",
  };

  if (req.headers["authorization"]) {
    headers["Authorization"] = req.headers["authorization"];
  }
  if (req.method !== "GET" && req.method !== "HEAD") {
    headers["Content-Type"] = req.headers["content-type"] || "application/json";
  }

  try {
    const body = await readBody(req);
    const upstream = await fetch(targetUrl, {
      method: req.method,
      headers,
      body,
    });

    const contentType = upstream.headers.get("content-type");
    if (contentType) res.setHeader("Content-Type", contentType);
    res.setHeader("Cache-Control", "no-store");

    const buf = Buffer.from(await upstream.arrayBuffer());
    return res.status(upstream.status).send(buf);
  } catch (err) {
    return res.status(502).json({
      success: false,
      proxyError: err.message || "Upstream API request failed",
    });
  }
};
