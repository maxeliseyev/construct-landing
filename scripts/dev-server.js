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

/** Compile a vercel `source` ("/c/:userId") into a matcher over the pathname. */
function compile(source) {
  const names = [];
  const pattern = source
    .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    .replace(/:([A-Za-z0-9_]+)/g, (_, name) => {
      names.push(name);
      return "([^/]+)";
    });
  return { re: new RegExp(`^${pattern}$`), names };
}

const redirects = (config.redirects || []).map((r) => ({ ...r, ...compile(r.source) }));
const rewrites = (config.rewrites || []).map((r) => ({ ...r, ...compile(r.source) }));

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
