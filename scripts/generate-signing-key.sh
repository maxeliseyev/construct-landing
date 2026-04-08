#!/usr/bin/env bash
# Generates Ed25519 keypair for relay config signing.
# Private key: signing_key.pem  (NEVER commit — in .gitignore)
# Public key:  signing_key.pub  (commit — embedded in iOS app)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRIV="$SCRIPT_DIR/signing_key.pem"
PUB="$SCRIPT_DIR/signing_key.pub"

if [[ -f "$PRIV" ]]; then
  echo "⚠️  $PRIV already exists. Delete it first if you want to regenerate."
  exit 1
fi

# Generate private key
openssl genpkey -algorithm ed25519 -out "$PRIV"
chmod 600 "$PRIV"

# Extract raw 32-byte public key in hex
openssl pkey -in "$PRIV" -pubout -outform DER \
  | tail -c 32 \
  | xxd -p -c 32 \
  > "$PUB"

echo "✅ Private key: $PRIV  (keep secret, never commit)"
echo "✅ Public key:  $PUB"
echo ""
echo "Public key hex:"
cat "$PUB"
echo ""
echo "Add this to Constants.swift:"
echo "  static let relayConfigSigningKey = \"$(cat "$PUB")\""
