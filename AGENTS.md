# AGENTS.md — construct-landing

The static public website (konstruct.cc): HTML, CSS and JS with self-hosted fonts, localized by JSON
dictionaries, deployed on Vercel. It makes factual claims about the product, so claims are checked
against the code, not remembered.

## Read first

| File | Why |
|---|---|
| `~/Code/construct-docs/decisions/rules-from-the-first-year.md` | why the rules exist |
| `README.md` (this repo) | pages, i18n, build, Vercel settings, CSP, caching, donations and PGP verification, security posture |
| `~/Code/construct-docs` | the vault; its own `AGENTS.md` is authoritative for structure and writing rules |

## The Zen of Konstruct

```
Someone has solved it before. Read them first.
The core decides; the app executes.
A message names the state it means. Time is not an address.
Reproduce, then fix.
One meaning, one carrier.
Bytes stay bytes.
Measure, then build.
The effect is the proof, not the exit code.
A test that cannot fail is worse than no test.
Boring before new.
Temporary is permanent, unless something checks it.
What nothing reads is not sent.
Silence is the worst failure: a message that never appears raises no error.
```

Canonical source: `~/Code/construct-docs/decisions/rules-from-the-first-year.md`. Change it there first.

## Rules

This repo has no protocol code, so only the rules that apply are listed; all twelve are in the vault note.

- **Reproduce, then fix.** A broken page or language switch is reproduced before it is changed.
- **One meaning, one carrier.** A fact lives in one place and `check-claims.py` re-derives it from the code; do not copy a number or a name into copy by hand.
- **Measure, then build.** Claims about networks, censorship or performance cite a measurement.
- **The effect is the proof.** A change is checked by `npm run check` and by what the deployed page serves.
- **A test that cannot fail is worse than none.** A new claim check is done when breaking the claim in the sibling repo reddens it.
- **Boring before new.** Static files, no framework, no third-party code.
- **Temporary has an end and a check.** No "fix later" without a date and something that notices.
- **Branch and PR, always** (below).

## Invariants of this repo

- **Check before pushing:** `npm run check` (`check-i18n.py`, `check-claims.py`, `build-locales.py --check`); after editing copy or styles run `python3 scripts/sync-versions.py`. Enable the pre-push hook once per clone: `git config core.hooksPath .githooks`.
- **A changed translation needs a new `I18N_CACHE_VER`** in `site.js`; `check-i18n.py` derives it. Without it browsers keep the old dictionary, which looks like a broken language switcher.
- **Every factual claim is pinned by `check-claims.py`** against `../construct-core`, `../construct-messenger`, `../construct-server` (SKIP if absent). The site once named a retired component as the production transport, a delivery status that does not exist, and the regions where circumvention works.
- **Two identity spaces:** the User ID is a server-random UUID; what is a hash of the identity key is the Device ID. Never write them as one thing.
- **No third-party requests** — no analytics, trackers, CDN or Google Fonts (JetBrains Mono is self-hosted in `fonts/`). CSP is `script-src 'self'`, `connect-src 'self'`; changing where scripts or locale JSON load from means changing CSP.
- **Product name is `Konstruct` in Latin** in every locale.

## Git and process

- **Never commit on `main`.** Topic branch (`feat|fix|docs|chore|test/<topic>`) from an up-to-date `main`, PR into it; `main` is what a release is built from. Agents push and open the PR only when asked.
- A commit made on `main` by mistake and not pushed moves with `git branch <topic> && git reset --keep origin/main && git switch <topic>`. Pushed history is never rewritten.
- Docs go in the vault (`~/Code/construct-docs`), not as ad-hoc markdown here. After work, progress goes into the task note `todo/NNN-*.md` («Ход»); a decision that constrains future work into `decisions/<slug>.md`; one line into `log.md`: `[YYYY-MM-DD HH:MM] note | <topic>`. A session log (`sessions/YYYY-MM-DD-<topic>.md`, with a mandatory `## Why`) only for a root cause or a rejected alternative.
