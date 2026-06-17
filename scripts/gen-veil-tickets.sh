#!/usr/bin/env bash
# gen-veil-tickets.sh — batch-generate N signed veil-front config links (+ QR SVGs)
# for testers. Each run of make-config-link mints a *fresh* random ticket
# (ticket_id + auth_key), so every tester gets a distinct, independently
# revocable-by-expiry capability.
#
# The Ed25519 issuer seed is derived from ./signing_key.pem and never leaves this
# repo. The derived public key is asserted against the value the iOS app pins
# (relayConfigSigningKey) so a wrong/rotated key fails loudly instead of minting
# links no client will trust.
#
# Usage:
#   bash scripts/gen-veil-tickets.sh [COUNT]
#   COUNT=20 DAYS=90 bash scripts/gen-veil-tickets.sh
#   bash scripts/gen-veil-tickets.sh 15 --out ~/Desktop/veil-tickets
#
# Output (default ./veil-tickets/):
#   veil-ticket-01.txt … link (konstruct://veil-config?d=…)
#   veil-ticket-01.svg … scannable QR
#   INDEX.md           … table of all links
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRIV="$SCRIPT_DIR/signing_key.pem"

# ── Defaults (must mirror ConstructMessenger Constants.swift) ─────────────────
# Relay 3 / veil-front (api.divany-kresla.uk). If the relay cert rotates, update
# SPKI here AND in Constants.swift (ruRelayPinnedSPKI) — they must match.
RELAY="${RELAY:-api.divany-kresla.uk:443}"
SNI="${SNI:-api.divany-kresla.uk}"
SPKI="${SPKI:-5621e47a745614de08efb054b01388f3bcf32c763ecf5f0aeaeb6b0785ff6861}"
SCOPE="${SCOPE:-}"
DAYS="${DAYS:-60}"
EXPECTED_PUBKEY="8a0ee71cd95f86a9f6877211accefaff6bb97f3051b3b2141f1c71690b9a2dcf"

# make-config-link binary (built from construct-veil).
VEIL_REPO="${VEIL_REPO:-$HOME/Code/construct-veil}"
BIN="${MAKE_CONFIG_LINK:-}"

# ── Args ──────────────────────────────────────────────────────────────────────
COUNT=10
OUT="$SCRIPT_DIR/veil-tickets"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)   OUT="$2"; shift 2 ;;
    --days)  DAYS="$2"; shift 2 ;;
    --relay) RELAY="$2"; shift 2 ;;
    --sni)   SNI="$2"; shift 2 ;;
    --spki)  SPKI="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,18p' "$0"; exit 0 ;;
    *) COUNT="$1"; shift ;;
  esac
done

# ── Preconditions ─────────────────────────────────────────────────────────────
[[ -f "$PRIV" ]] || { echo "❌ signing key not found: $PRIV"; exit 1; }
command -v openssl >/dev/null || { echo "❌ openssl required"; exit 1; }

# Locate (or build) make-config-link.
if [[ -z "$BIN" ]]; then
  if [[ -x "$VEIL_REPO/target/release/make-config-link" ]]; then
    BIN="$VEIL_REPO/target/release/make-config-link"
  elif [[ -x "$VEIL_REPO/target/debug/make-config-link" ]]; then
    BIN="$VEIL_REPO/target/debug/make-config-link"
  else
    echo "ℹ️  make-config-link not built — building (debug)…"
    ( cd "$VEIL_REPO" && cargo build --bin make-config-link )
    BIN="$VEIL_REPO/target/debug/make-config-link"
  fi
fi
[[ -x "$BIN" ]] || { echo "❌ make-config-link not found/executable: $BIN"; exit 1; }

# Derive the Ed25519 seed (last 32 bytes of the PKCS8 DER) and assert the public
# key matches what the app pins.
SEED="$(openssl pkey -in "$PRIV" -outform DER 2>/dev/null | tail -c 32 | xxd -p -c 32)"
DERIVED_PUB="$(openssl pkey -in "$PRIV" -pubout -outform DER 2>/dev/null | tail -c 32 | xxd -p -c 32)"
if [[ "$DERIVED_PUB" != "$EXPECTED_PUBKEY" ]]; then
  echo "❌ signing_key.pem pubkey ($DERIVED_PUB) != app relayConfigSigningKey ($EXPECTED_PUBKEY)"
  echo "   These links would not be trusted by the app. Aborting."
  exit 1
fi

mkdir -p "$OUT"
INDEX="$OUT/INDEX.md"
{
  echo "# VEIL tester links"
  echo
  echo "- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Relay: \`$RELAY\` (SNI \`$SNI\`)"
  echo "- SPKI: \`$SPKI\`"
  echo "- Valid: $DAYS days"
  echo "- Issuer pubkey: \`$DERIVED_PUB\`"
  echo
  echo "| # | Link | QR |"
  echo "|---|------|----|"
} > "$INDEX"

echo "Generating $COUNT tester link(s) → $OUT"
for i in $(seq 1 "$COUNT"); do
  n=$(printf "%02d" "$i")
  svg="$OUT/veil-ticket-$n.svg"
  txt="$OUT/veil-ticket-$n.txt"
  # Link → stdout (captured); diagnostics + terminal QR → stderr (discarded).
  link="$("$BIN" \
    --signing-key "$SEED" \
    --relay "$RELAY" \
    --sni "$SNI" \
    --spki "$SPKI" \
    --scope "$SCOPE" \
    --days "$DAYS" \
    --qr-svg "$svg" \
    2>/dev/null)"
  printf '%s\n' "$link" > "$txt"
  printf '| %s | [link](veil-ticket-%s.txt) | ![qr](veil-ticket-%s.svg) |\n' "$n" "$n" "$n" >> "$INDEX"
  echo "  [$n] $link"
done

echo
echo "✅ $COUNT links in $OUT  (index: $INDEX)"
echo "   Each tester opens one link on the device (or scans its .svg QR)."
