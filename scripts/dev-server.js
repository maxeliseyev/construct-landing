#!/usr/bin/env node
/**
 * Local preview server for the site. No dependencies.
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
 * So this reads vercel.json rather than restating it: redirects, rewrites
 * (including `:param` and `:param(a|b)` segments) and headers all come from the
 * file production is configured with. What it deliberately does not do is
 * guess — `cleanUrls` is false in vercel.json, so /privacy resolves only
 * because a rewrite says so, and a path with no rewrite 404s here just as it
 * would live.
 *
 * It serves dist/, the output of scripts/build-locales.py — the same build
 * Vercel runs — and rebuilds it before answering whenever a source file is
 * newer than the last build, so an edit shows on the next reload.
 */
"use strict";

const fs = require("fs");
const http = require("http");
const path = require("path");
const { spawnSync } = require("child_process");

const REPO = path.resolve(__dirname, "..");
const ROOT = path.join(REPO, "dist");

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
  ".xml": "application/xml; charset=utf-8",
  ".md": "text/plain; charset=utf-8",
  ".asc": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json",
};

const config = JSON.parse(fs.readFileSync(path.join(REPO, "vercel.json"), "utf8"));

/* Newest modification time among the inputs to the build. dist/ and .git are
   outputs and bookkeeping, not inputs. */
function newestSource(dir = REPO) {
  let newest = 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (["dist", ".git", "node_modules", "target"].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    const time = entry.isDirectory() ? newestSource(full) : fs.statSync(full).mtimeMs;
    if (time > newest) newest = time;
  }
  return newest;
}

let builtAt = 0;
let buildError = null;

/* What .vercelignore withholds and what the build drops never reach dist/, so
   a withdrawn page 404s here the way it does live without a second list. */
function ensureBuilt() {
  const newest = newestSource();
  if (builtAt && newest <= builtAt) return;
  const started = Date.now();
  const res = spawnSync("python3", [path.join(REPO, "scripts/build-locales.py")], {
    cwd: REPO,
    encoding: "utf8",
  });
  builtAt = started;
  buildError = res.status === 0 ? null : (res.stdout || "") + (res.stderr || "");
  console.log(res.status === 0 ? "rebuilt dist/" : "BUILD FAILED\n" + buildError);
}

/**
 * Compile a vercel `source` into a matcher over the pathname. The forms that
 * occur: `:param` segments ("/c/:userId"), constrained ones with an optional
 * marker ("/:lang(ru|uk)/:page(faq|roadmap)?" — the trailing `?` makes the
 * whole `/segment` optional, as in path-to-regexp) and `(.*)` wildcards in
 * header rules ("/fonts/(.*)"). Literal text between them is escaped.
 */
function compile(source) {
  const names = [];
  const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const token = /(\/?):([A-Za-z0-9_]+)(?:\(([^)]*)\))?(\?)?|\(\.\*\)/g;
  let pattern = "";
  let last = 0;
  for (const m of source.matchAll(token)) {
    pattern += escape(source.slice(last, m.index));
    last = m.index + m[0].length;
    if (m[0] === "(.*)") {
      pattern += "(.*)";
      continue;
    }
    const [, slash, name, constraint, optional] = m;
    names.push(name);
    const group = `(${constraint || "[^/]+"})`;
    pattern += optional ? `(?:${escape(slash)}${group})?` : escape(slash) + group;
  }
  pattern += escape(source.slice(last));
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
    (out, name, i) => out.split(`:${name}`).join(encodeURIComponent(match[i + 1] || "")),
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
  ensureBuilt();
  if (buildError) {
    log(req, 500, "build failed");
    return send(res, 500, "scripts/build-locales.py failed:\n\n" + buildError, {
      "Content-Type": "text/plain; charset=utf-8",
    });
  }
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
  console.log("Serving dist/ — rebuilt from the sources whenever they change.\n");
});
