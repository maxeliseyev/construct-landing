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
npx vercel dev                   # to also exercise vercel.json rewrites/headers
```

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

> **Known CSP note:** `script-src` still allows `'unsafe-inline'` because the crypto demo and the
> language switcher use inline event handlers. It still blocks *external* and injected scripts. Moving
> to strict `script-src 'self'` (A+) requires externalising the inline JS.

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
