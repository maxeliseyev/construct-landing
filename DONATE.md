# Support Konstruct

Konstruct takes **no ads, no data resale, and no telemetry** — so it runs on
voluntary donations. Donations fund development and the server directly.

These addresses are the canonical source of truth. If an address shown on the
website (konstruct.cc) ever differs from what is committed here in git history,
**trust this file, not the page** — a static site can be tampered with.

## Monero (XMR) — recommended

Prefer Monero if you value privacy: unlike Bitcoin its chain is not public, so
your donation is not linkable and the balance is not visible.

```
496i5qvPzRtJPQjiPXnLvEGutjHFth4pWDQaJwbbMreyaTYg4qfbo48MXrTnYH32MHiAn5GcSEN1c48EYBvVkrx9Pi5BWvn
```

## Bitcoin (BTC)

```
bc1q5cthgu6k9utg9hk2mx2xshdtsrhvu54ysmqhmm
```

> Note on Bitcoin privacy: the BTC address is static and its chain is public, so
> donations to it are linkable and the balance is visible on-chain. That is a
> property of Bitcoin, not a choice we can hide — use Monero if this matters to
> you.

## Ko-fi (card / PayPal) — convenient, not private

For a one-off or recurring donation by card or PayPal:

<https://ko-fi.com/construct_msg>

> Note: fiat payments are **not anonymous** — the payment processor (Ko-fi,
> Stripe, PayPal) knows your identity. Use Monero if you want a private donation.
> This option exists only to lower the barrier for people who don't use crypto.

## Verify this file (PGP)

This file is signed, so you can confirm the addresses are authentic even if the site or repo is
tampered with:

```bash
gpg --import KEYS.asc          # the project signing key (also served at konstruct.cc/KEYS.asc)
gpg --fingerprint              # compare against the fingerprint published in README.md and on the site
gpg --verify DONATE.md.asc DONATE.md
```

A "Good signature" means the addresses above are the maintainer's. If it fails, **do not send** —
the signature covers this exact file, so any change to an address invalidates it.

