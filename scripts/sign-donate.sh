#!/usr/bin/env bash
#
# Sign DONATE.md so donors can verify addresses cryptographically.
# Produces a detached signature (DONATE.md.asc) and exports the public key (KEYS.asc).
# DONATE.md itself stays plain markdown (renders on GitHub).
#
# Usage:
#   scripts/sign-donate.sh [KEY_ID_OR_EMAIL]
#
# If KEY_ID_OR_EMAIL is omitted, gpg uses your default signing key.
# Run from the repo root. Commit DONATE.md, DONATE.md.asc and KEYS.asc together.

set -euo pipefail

cd "$(dirname "$0")/.."

KEY="${1:-}"
FILE="DONATE.md"

[ -f "$FILE" ] || { echo "error: $FILE not found (run from repo root)"; exit 1; }

echo "==> Detached-signing $FILE"
if [ -n "$KEY" ]; then
  gpg --local-user "$KEY" --armor --yes --detach-sign --output "$FILE.asc" "$FILE"
else
  gpg --armor --yes --detach-sign --output "$FILE.asc" "$FILE"
fi

echo "==> Exporting public key to KEYS.asc"
if [ -n "$KEY" ]; then
  gpg --armor --export "$KEY" > KEYS.asc
else
  # Export the key that just signed (whatever gpg picked as default-key).
  SIGNER=$(gpg --verify "$FILE.asc" "$FILE" 2>&1 | grep -oE '[0-9A-F]{16,40}' | head -1 || true)
  gpg --armor --export ${SIGNER:-} > KEYS.asc
fi

echo "==> Verifying (dry run)"
gpg --verify "$FILE.asc" "$FILE"

echo
echo "Fingerprint to publish in README.md, on the site, and elsewhere:"
gpg --fingerprint ${KEY:-} | grep -A1 'pub\|sec' | grep -oE '([0-9A-F]{4} *){10}' | head -1 || gpg --fingerprint ${KEY:-}
echo
echo "Done. Commit: git add DONATE.md DONATE.md.asc KEYS.asc && git commit -m 'chore: sign donation addresses'"
