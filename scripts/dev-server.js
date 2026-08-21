#!/usr/bin/env node
/**
 * Local preview server for the static site. No dependencies, no build step.
 *
 *     npm run dev            # http://localhost:8000
 *     npm run dev -- 3000    # another port
 *
 * `python3 -m http.server` also serves the files, but it serves them at the
 * wrong addresses: production reaches the sub-pages through the rewrites in
 * vercel.json, so /faq is a 404 under a plain file server and every nav link
 * has to be clicked as /faq.html instead. A preview that answers differently
 * from production is a preview you cannot trust for exactly the questions you
 * open it to answer — which page a link lands on, whether /crypto still
 * redirects, whether a withdrawn file is reachable.
 *
 * So this reads vercel.json and .vercelignore rather than restating them:
 * redirects, rewrites (including `:param` segments) and the deployment
 * exclusions all come from the files that production is configured with. What
 * it deliberately does not do is guess — `cleanUrls` is false in vercel.json,
 * so /privacy resolves only because a rewrite says so, and a path with no
 * rewrite 404s here just as it would live.
 */
"use strict";

const fs = require("fs");
const http = require("http");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8",
  ".md": "text/plain; charset=utf-8",
  ".asc": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json",
};

const config = JSON.parse(fs.readFileSync(path.join(ROOT, "vercel.json"), "utf8"));

/* Files listed in .vercelignore are in git but not on the site — crypto.* was
   withdrawn, not deleted. Serving them locally would show a page that no
   visitor can reach. */
const ignored = new Set(
  fs
    .readFileSync(path.join(ROOT, ".vercelignore"), "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"))
);

/**
 * Compile a vercel `source` into a matcher over the pathname. Two forms occur:
 * `:param` segments in rewrites ("/c/:userId") and `(.*)` wildcards in header
 * rules ("/fonts/(.*)"). Splitting on the wildcard keeps it out of the escape
 * pass entirely, so there is no sentinel to collide with anything.
 */
function compile(source) {
  const names = [];
  const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = source
    .split("(.*)")
    .map((part) =>
      escape(part).replace(/:([A-Za-z0-9_]+)/g, (_, name) => {
        names.push(name);
        return "([^/]+)";
      })
    )
    .join("(.*)");
  return { re: new RegExp(`^${pattern}$`), names };
}

const redirects = (config.redirects || []).map((r) => ({ ...r, ...compile(r.source) }));
const rewrites = (config.rewrites || []).map((r) => ({ ...r, ...compile(r.source) }));
const headerRules = (config.headers || []).map((r) => ({ ...r, ...compile(r.source) }));

/**
 * Every matching header rule applies, in file order, later keys winning — the
 * same way Vercel layers the catch-all security headers under the per-asset
 * ones. Matched against the requested path, before rewrites, because that is
 * the path the rules are written against.
 */
/**
 * Three of production's headers describe an HTTPS origin and cannot be honoured
 * by a plain-HTTP preview:
 *
 *   Cache-Control            production wants a year on the fonts; a preview
 *                            that obeys it stops showing you your own edits,
 *                            which is the one thing it is for.
 *   Strict-Transport-Security  nothing to enforce off HTTPS, and it is exactly
 *                            the kind of header that outlives the session that
 *                            set it.
 *   upgrade-insecure-requests  rewrites every subresource to https://. Chrome
 *                            exempts localhost, so this looks harmless until
 *                            the preview is opened on a LAN address (a phone,
 *                            another machine) — and then the CSS, the scripts,
 *                            the fonts and the images all fail at once with
 *                            ERR_SSL_PROTOCOL_ERROR and the site renders as
 *                            unstyled HTML.
 *
 * The rest of the CSP stays. Keeping it is the point: it is what makes a local
 * preview refuse the same things production refuses, so a violation is found
 * here rather than after a deploy.
 */
function headersFor(pathname) {
  const out = {};
  for (const rule of headerRules) {
    if (!rule.re.test(pathname)) continue;
    for (const h of rule.headers) out[h.key] = h.value;
  }

  delete out["Cache-Control"];
  delete out["Strict-Transport-Security"];

  if (out["Content-Security-Policy"]) {
    const kept = out["Content-Security-Policy"]
      .split(";")
      .map((d) => d.trim())
      .filter((d) => d && d !== "upgrade-insecure-requests");
    out["Content-Security-Policy"] = kept.join("; ");
  }

  return out;
}

/** Substitute captured `:param` values into a destination. */
function expand(destination, names, match) {
  return names.reduce(
    (out, name, i) => out.split(`:${name}`).join(encodeURIComponent(match[i + 1])),
    destination
  );
}

function findMatch(rules, pathname) {
  for (const rule of rules) {
    const match = rule.re.exec(pathname);
    if (match) return { rule, target: expand(rule.destination, rule.names, match) };
  }
  return null;
}

function send(res, status, body, headers = {}) {
  res.writeHead(status, { "Cache-Control": "no-store", ...headers });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  let pathname = decodeURIComponent(url.pathname);
  const configured = headersFor(pathname);

  const redirect = findMatch(redirects, pathname);
  if (redirect) {
    const status = redirect.rule.permanent ? 308 : 307;
    log(req, status, pathname + " -> " + redirect.target);
    return send(res, status, "", { Location: redirect.target });
  }

  const rewrite = findMatch(rewrites, pathname);
  if (rewrite) {
    const [target, query] = rewrite.target.split("?");
    pathname = target;
    for (const [k, v] of new URLSearchParams(query || "")) url.searchParams.set(k, v);
  }

  if (pathname.endsWith("/")) pathname += "index.html";

  /* Resolve first, then check containment: `..` in a request must not reach
     outside the repo, and comparing the resolved path is the only check that
     cannot be walked around with encoding. */
  const file = path.resolve(ROOT, "." + pathname);
  if (file !== ROOT && !file.startsWith(ROOT + path.sep)) {
    log(req, 403, pathname);
    return send(res, 403, "403 Forbidden");
  }

  if (ignored.has(path.relative(ROOT, file))) {
    log(req, 404, pathname + " (in .vercelignore — not deployed)");
    return send(res, 404, "404 Not Found — this file is in .vercelignore");
  }

  fs.readFile(file, (err, body) => {
    if (err) {
      log(req, 404, pathname);
      return send(res, 404, "404 Not Found");
    }
    log(req, 200, pathname);
    send(res, 200, body, {
      "Content-Type": MIME[path.extname(file).toLowerCase()] || "application/octet-stream",
      // Configured headers last: vercel.json is the authority on Content-Type
      // for the paths where it sets one (the .well-known files have no
      // extension to guess from, and speculation rules need their own type).
      ...configured,
    });
  });
});

function log(req, status, detail) {
  console.log(`${String(status).padEnd(3)} ${req.method} ${detail}`);
}

const port = Number(process.argv[2] || process.env.PORT || 8000);
server.listen(port, () => {
  console.log(`konstruct-landing → http://localhost:${port}`);
  console.log("Open it over http, not file:// — site.js fetches /i18n/{lang}.json.\n");
});
