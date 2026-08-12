# Konstruct — Website

Source of the Konstruct marketing/landing site, served at **[konstruct.cc](https://konstruct.cc)**.
Static HTML/CSS/JS, deployed on Vercel. Part of the [Konstruct](https://github.com/konstruct-msg)
privacy-first, end-to-end-encrypted messenger project.

## Pages

| Path | File | What |
|------|------|------|
| `/` | `index.html` | Landing: mission, architecture, no-telemetry, support |
| `/faq` | `faq.html` | Frequently asked questions (EN/RU/JA) |
| `/privacy` | `privacy.html` | Privacy policy |
| `/crypto` | `crypto.html` | Interactive cryptography demo |
| `/c/:userId` | `contact.html` | Contact deep-link landing |

There is **no build step**. Copy for `index` / `faq` lives in JSON locale files:

```
i18n/en.json
i18n/ru.json
i18n/ja.json
```

HTML uses a single tree with `data-i18n` / `data-i18n-html` keys. `site.js`
auto-detects the language (`navigator.languages` + `localStorage`), fetches
`/i18n/{lang}.json` (sessionStorage-cached), and applies strings. English text
remains in the HTML as a no-JS / failed-fetch fallback. Language chrome is the
HUD dropdown `LANG::XX ▾`.

```bash
python3 scripts/check-i18n.py   # key parity + HTML refs
# optional re-extract from class-based HTML (legacy):
# python3 scripts/migrate-i18n.py
```

## Local preview

It is a static site — no bundler. Any static server works:

```bash
python3 -m http.server 8000      # then open http://localhost:8000
# or
npx vercel dev                   # exercises vercel.json rewrites + headers (needs CLI login)
```

**Important for i18n:** open via `http://localhost:…`, not `file://`.  
`site.js` loads `/i18n/{lang}.json` with `fetch`; that only works over HTTP(S) same-origin.

## Deploy on Vercel

This repo is a **static** project. There is no `package.json` and no build output directory.

### Dashboard settings (Project → Settings → General / Build & Development)

| Setting | Value |
|---------|--------|
| **Framework Preset** | Other |
| **Build Command** | *(empty / disabled)* |
| **Output Directory** | *(empty / `.` / leave default for static root)* |
| **Install Command** | *(empty / disabled)* |
| **Root Directory** | `.` (repo root) |
| **Node.js Version** | any (unused; no build) |

Do **not** set Output Directory to `dist` or `public` — HTML/JS/CSS/`i18n/` live at the repository root.

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
| `/` | `index.html` | Landing |
| `/faq` | rewrite → `faq.html` | see `vercel.json` |
| `/privacy`, `/crypto`, `/add` | rewrites | same pattern |
| `/c/:userId` | rewrite → `contact.html` | deep link |
| `/site.js`, `/effects.js` | static | language switcher + HUD effects |
| `/i18n/en.json`, `/i18n/ru.json`, `/i18n/ja.json` | static | **required** for non-EN locales |
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

`site.js` also keeps a **sessionStorage** dictionary cache keyed by  
`construct-i18n-v1-{lang}`. After a large copy rewrite, bump `I18N_CACHE_VER` in `site.js` so open tabs drop the old dictionary.

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

1. Open DevTools → Network → reload. Expect `i18n/en.json` (or `ru`/`ja` from auto-detect).
2. Switch `LANG::` to JA / RU — body text and `document.title` update without full reload.
3. Hard-refresh; no CSP errors on `fetch` of `/i18n/*.json`.
4. Disable JS briefly: English fallback text in HTML remains visible.

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
