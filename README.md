# Konstruct — Website

Source of the Konstruct marketing/landing site, served at **[konstruct.cc](https://konstruct.cc)**.
Static HTML/CSS/JS, deployed on Vercel. Part of the [Konstruct](https://github.com/konstruct-msg)
privacy-first, end-to-end-encrypted messenger project.

## Pages

| Path | File | What |
|------|------|------|
| `/` | `index.html` | Landing: mission, architecture, no-telemetry, support |
| `/faq` | `faq.html` | Frequently asked questions |
| `/technical` | `technical.html` | How it works |
| `/roadmap` | `roadmap.html` | Done / in progress / planned |
| `/privacy` | `privacy.html` | Privacy policy |
| `/add` | `add.html` | Invite-link landing (iOS Universal Link path) |
| ~~`/crypto`~~ | `crypto.html` | **Withdrawn** — in `.vercelignore`, `/crypto` redirects to `/faq` |
| `/c/:userId` | `contact.html` | Contact deep-link landing |

Every content page exists once per language, at its own URL: English unprefixed
(`/faq`), the others under their code (`/ru/faq`, `/tr/`, `/uk/privacy`, …). `/add`
and `/c/:userId` are not prefixed — the app's links point at them — and translate at
runtime instead.

Copy lives in JSON locale files; Russian is the reference text:

```
i18n/en.json
i18n/ru.json
i18n/ja.json
i18n/hy.json
i18n/fr.json
i18n/uk.json
i18n/tr.json
```

Each page is one HTML file with `data-i18n` / `data-i18n-html` keys and English text.
`scripts/build-locales.py` (stdlib Python, run by Vercel on deploy) renders `dist/`:
every page × language with the text filled in, `<html lang>`, title and description
(`<page>.meta.title` / `.meta.description`), link-preview tags, canonical and
`hreflang`, links kept inside the language, and the `LANG::XX ▾` switcher as plain
links. Plus `sitemap.xml`, `robots.txt` and `speculation-rules.json`. It verifies its
own output against the dictionaries and fails the deploy if anything is off.

Languages not yet read by a native speaker (`REVIEWED` in the build script — today
everything except `en` and `ru`) are built and reachable but `noindex`, and left out
of the sitemap and `hreflang`.

A first visit to an English page goes to the reader's language: `lang-redirect.js`
(synchronous, top of `<head>`) uses the language last chosen in the switcher, else
the browser's list. It never redirects from a prefixed page. No geolocation.

```bash
npm run build                    # -> dist/
python3 scripts/sync-versions.py # after editing copy or styles — recompute cache markers
npm run check                    # everything below
python3 scripts/check-i18n.py    # key parity, markup-in-textContent, cache markers
python3 scripts/check-claims.py  # every factual claim, re-derived from the sibling repos
python3 scripts/build-locales.py --check  # build into a temp dir and verify every page
# optional re-extract from class-based HTML (legacy):
# python3 scripts/migrate-i18n.py
```

### Enable the pre-push hook

All three run on `git push`. `core.hooksPath` is local config, so a fresh clone
needs this once:

```bash
git config core.hooksPath .githooks
```

`check-claims.py` reads `../construct-core`, `../construct-messenger` and
`../construct-server`; without them it reports SKIP rather than failing. It exists
because the site published several things that were not true — a retired component
named as the production transport, a delivery status that does not exist, and the
regions where censorship circumvention currently works. `check-i18n.py` also derives
`I18N_CACHE_VER` in `site.js` from the locale contents: change a translation without
it and browsers keep serving the old dictionary, which looks like the language
switcher being broken.

## Local preview

No bundler, no dependencies to install — `python3` and `node`.

```bash
npm run dev                      # then open http://localhost:8000
npm run dev -- 3000              # another port
```

`scripts/dev-server.js` is plain Node with no packages behind it. It serves `dist/`
and re-runs the build before answering whenever a source file is newer, so an edit
shows on reload. It reads `vercel.json`, so the preview answers on the same
addresses as production: `/faq` and `/ru/faq` resolve through the rewrites
(`cleanUrls` is `false`, so *only* through them), `/crypto` still redirects, and
files withdrawn from the deployment stay 404 locally too.

To test the first-visit redirect, use a browser profile whose language is not
English, or clear `construct-lang` from localStorage after using the switcher.

## Deploy on Vercel

`vercel.json` sets `buildCommand: python3 scripts/build-locales.py` and
`outputDirectory: dist`; those override the dashboard. The build image has Python
3.12 (checked 2026-10-12), so the script stays stdlib-only and 3.12-compatible.
Only `dist/` is served — `scripts/`, `.githooks/` and the like are not published.

The `package.json` at the root is a local convenience only — `dev`, `build`,
`check` — with no dependencies. It is listed in `.vercelignore` so it never reaches
the builder: an uploaded `package.json` is what makes Vercel run an install step,
and this project has nothing to install.

### Dashboard settings (Project → Settings → General / Build & Development)

| Setting | Value |
|---------|--------|
| **Framework Preset** | Other |
| **Build / Output / Install** | leave default — `vercel.json` decides |
| **Root Directory** | `.` (repo root) |

### First-time link (CLI)

```bash
# from repo root
npx vercel login
npx vercel link          # bind to the existing konstruct.cc project
npx vercel --prod        # production deploy
```

Git integration: push to `main` → production deploy (if the project is already connected to this GitHub repo).

### What production must serve

| URL | Source | Notes |
|-----|--------|--------|
| `/` | `dist/index.html` | Landing |
| `/faq` | rewrite → `faq.html` | see `vercel.json` |
| `/ru`, `/ru/faq`, … | rewrites → `dist/<lang>/…` | one per language and page |
| `/sitemap.xml`, `/robots.txt` | generated | reviewed languages only |
| `/privacy`, `/add` | rewrites | same pattern (`/crypto` is a 307 to `/faq`) |
| `/c/:userId` | rewrite → `contact.html` | deep link |
| `/site.js`, `/effects.js` | static | language switcher + HUD effects |
| `/i18n/en.json`, `/i18n/ru.json`, `/i18n/ja.json`, `/i18n/hy.json`, `/i18n/fr.json`, `/i18n/uk.json`, `/i18n/tr.json` | static | **required** for non-EN locales |
| `/fonts/*`, `/styles.css`, `/effects.css` | static | self-hosted assets |

If `/i18n/ja.json` returns 404, Japanese (and any non-fallback language) will not apply — English HTML fallback still shows.

### CSP and i18n fetch

`vercel.json` sets:

```
connect-src 'self'
```

Locale JSON is same-origin only. Do not host `i18n/` on another domain without updating CSP.

### Caching (after i18n)

| Path | Cache-Control |
|------|----------------|
| `/i18n/*.json` | `max-age=60, stale-while-revalidate=86400` — copy can change every deploy |
| `/site.js`, `/effects.js` | same short TTL |
| `/fonts/*`, images (`favicon`, `og-image`) | long `immutable` |
| `/styles.css`, `/effects.css`, `/contact.css` | short TTL (`max-age=60`) — **not** immutable (no content hash in URL) |

`site.js` keeps a **sessionStorage** dictionary cache keyed by `I18N_CACHE_VER`, and the pages
carry `?v=` on `styles.css` and `site.js`. All three are **content hashes**, not hand-typed —
`scripts/sync-versions.py` recomputes them and `check-i18n.py` fails when one is stale. This is
not optional bookkeeping: editing copy without moving the marker leaves browsers on the old
dictionary, which presents as the language switcher being broken, and editing CSS without moving
it leaves them on the old stylesheet.

### Post-deploy smoke checklist

```bash
# 1. HTML + rewrite
curl -sI https://konstruct.cc/ | head -5
curl -sI https://konstruct.cc/faq | head -5

# 2. Locale files (must be 200 + application/json)
curl -sI https://konstruct.cc/i18n/en.json
curl -sI https://konstruct.cc/i18n/ru.json
curl -sI https://konstruct.cc/i18n/ja.json

# 3. Scripts
curl -sI https://konstruct.cc/site.js

# 4. CSP still blocks third-party connect (optional)
curl -sI https://konstruct.cc/ | grep -i content-security
```

In the browser (production):

1. `view-source:https://konstruct.cc/ru/faq` — Russian in the HTML itself, `lang="ru"`.
2. Switch `LANG::` to JA — the URL becomes `/ja/…`; switch back to EN — it stays English on reload.
3. With a non-English browser and no saved choice, `/` lands on `/<lang>`.
4. `/add` in a Russian browser shows Russian (runtime translation still works there).

### Domains

Production hostname: **konstruct.cc** (and `www` if configured).  
Apex + www should both point at the same Vercel project; SSL is automatic.

### Local env / secrets

None required for the marketing site. Do not put signing private keys or deploy secrets in the Vercel project env for this static frontend.

## Security & privacy posture

This site practises what the product preaches (see
[`compliance/no-telemetry-manifesto.md`](https://github.com/konstruct-msg) in the docs):

- **No third-party requests.** No analytics, no trackers, no CDN. Fonts (JetBrains Mono) are
  **self-hosted** in `fonts/` — Google Fonts would leak every visitor's IP.
- **No telemetry.** Nothing about a visitor is collected or transmitted.
- **Security headers** (`vercel.json`): Content-Security-Policy, HSTS, `X-Content-Type-Options`,
  `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy`. Scores **A** on
  securityheaders.com (capped only by a pragmatic `script-src 'unsafe-inline'` — see below).
- **Static only** — no server-side code, minimal attack surface.

> **CSP:** global policy is `script-src 'self'` and `connect-src 'self'` (locale JSON is same-origin).
> `style-src` still allows `'unsafe-inline'` for a few page-local `<style>` blocks. Do not load
> scripts or i18n dictionaries from a third-party host without changing CSP.

## Donations

Konstruct takes no ads and sells no data, so it runs on donations. Addresses live in
**[`DONATE.md`](DONATE.md)** — that file (and its git history) is the **canonical source of truth**.

### Verifying a donation address (PGP)

`DONATE.md` is signed so you can confirm an address is authentic even if this site or repo is
tampered with. To verify:

```bash
# 1. Import the project signing key
gpg --import KEYS.asc

# 2. Confirm the fingerprint matches the one published independently
#    (this README, the website, and the maintainer's other channels):
#    13AC BE18 0D7B 20A2 4D2D  D6B0 99DD 3ECE 736F 0672
gpg --fingerprint

# 3. Verify the signature over DONATE.md
gpg --verify DONATE.md.asc DONATE.md
# → "Good signature from ..." means the addresses are authentic.
```

If verification fails, **do not send** — cross-check against another channel and report it.

## Contributing / security

- Issues and PRs: <https://github.com/konstruct-msg>
- Report a security issue privately:
  <https://github.com/konstruct-msg/construct-core/security/advisories/new>

## License

Site **content/text** is CC-BY-4.0. Code follows the Konstruct project's per-component licensing
(see the main organisation). A `LICENSE` file should accompany this repository.
