#!/usr/bin/env bash
# Signs .well-known/construct-server with Ed25519 private key.
# Usage: bash scripts/sign-config.sh
#
# Signing format:
#   1. Read JSON, remove "signature" field (if present)
#   2. Canonicalize: compact JSON, keys sorted
#   3. Sign canonical bytes with Ed25519 → base64url
#   4. Insert signature back into file
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$REPO_DIR/.well-known/construct-server"
PRIV="$SCRIPT_DIR/signing_key.pem"

if [[ ! -f "$PRIV" ]]; then
  echo "❌ Private key not found: $PRIV"
  echo "   Run: bash scripts/generate-signing-key.sh"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "❌ python3 required for JSON canonicalization"
  exit 1
fi

# Step 1: Canonical JSON (no signature field, sorted keys, compact)
CANONICAL=$(python3 - "$CONFIG" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
data.pop("signature", None)
# Update signed_at timestamp
from datetime import datetime, timezone
data["signed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps(data, sort_keys=True, separators=(',', ':')), end='')
PYEOF
)

# Step 2: Sign with Ed25519 (via temp file — openssl pkeyutl requires seekable input)
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT
echo -n "$CANONICAL" > "$TMPFILE"
SIG=$(openssl pkeyutl -sign -inkey "$PRIV" -in "$TMPFILE" -rawin \
  | base64 | tr '+/' '-_' | tr -d '=\n')

# Step 3: Write back with signature inserted
python3 - "$CONFIG" "$CANONICAL" "$SIG" <<'PYEOF'
import json, sys
config_path, canonical_str, sig = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.loads(canonical_str)
data["signature"] = "ed25519:" + sig
with open(config_path, 'w') as f:
    json.dump(data, f, indent=2, sort_keys=True)
    f.write('\n')
PYEOF

echo "✅ Signed config: $CONFIG"
echo "   Signature: ed25519:${SIG:0:20}..."
echo ""
echo "Next steps:"
echo "  git add .well-known/construct-server"
echo "  git commit -m 'chore: update relay config + resign'"
echo "  git push  # Vercel deploys automatically"
