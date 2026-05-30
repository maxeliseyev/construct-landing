#!/usr/bin/env python3
"""
VEIL relay smoke test — validates the full relay pipeline health:

  1. TCP reachability — MSK relay, AMS relay, main gRPC server
  2. TLS SPKI pins   — fetch live cert from each relay, compare with known pins
  3. .well-known     — fetch config, verify Ed25519 signature, check embedded SPKIs
  4. Consistency     — SPKI in .well-known matches what the relay server actually serves

Usage:
  python3 tests/veil_smoke_test.py          # human-readable output
  python3 tests/veil_smoke_test.py --ci     # exit 1 if any check fails (for CI)
  python3 tests/veil_smoke_test.py --json   # JSON output for programmatic use

Requirements:
  cryptography>=3.0  (for Ed25519 signature verification)
  pip install cryptography
"""

import hashlib
import json
import socket
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ── Configuration ─────────────────────────────────────────────────────────────

WELL_KNOWN_URL = "https://konstruct.cc/.well-known/construct-server"

RELAYS = [
    {
        "id": "msk",
        "addr": "158.160.140.67",
        "port": 443,
        "sni": "storage.yandexcloud.net",
        # Hardcoded SPKI from Constants.swift — source of truth for MSK
        "spki_hardcoded": "ce2bbfcac1fffab1f4f41ee540aee2dea92c523f7768264aeb87184bf8bfa723",
    },
    {
        "id": "ams",
        "addr": "ice.ams.konstruct.cc",
        "port": 443,
        "sni": "ice.ams.konstruct.cc",
        "spki_hardcoded": None,  # AMS cert is CA-signed, no pin
    },
]

MAIN_SERVER = {"addr": "ams.konstruct.cc", "port": 443}

# Ed25519 public key (hex) — matches VEILConfig.relayConfigSigningKey in Constants.swift
SIGNING_PUBLIC_KEY_HEX = (
    "8a0ee71cd95f86a9f6877211accefaff6bb97f3051b3b2141f1c71690b9a2dcf"
)

TIMEOUT = 10  # seconds

# ── Result tracking ────────────────────────────────────────────────────────────


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""
    warning: bool = False  # pass but something looks off


@dataclass
class Suite:
    name: str
    checks: list = field(default_factory=list)

    def add(
        self, name: str, passed: bool, detail: str = "", warning: bool = False
    ) -> bool:
        self.checks.append(Check(name, passed, detail, warning))
        return passed

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)


# ── Helpers ────────────────────────────────────────────────────────────────────


def fetch_spki(addr: str, port: int, sni: str) -> Optional[str]:
    """Connect via TLS, extract SHA-256 of SubjectPublicKeyInfo (same as openssl dgst)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # we compute pin ourselves
    try:
        with socket.create_connection((addr, port), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=sni) as tls:
                der = tls.getpeercert(binary_form=True)
                if not der:
                    return None
                # Parse SubjectPublicKeyInfo out of DER cert using cryptography if available
                try:
                    from cryptography import x509
                    from cryptography.hazmat.primitives import serialization

                    cert = x509.load_der_x509_certificate(der)
                    pub_der = cert.public_key().public_bytes(
                        serialization.Encoding.DER,
                        serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
                    return hashlib.sha256(pub_der).hexdigest()
                except ImportError:
                    pass
                # Fallback: call openssl in subprocess (always available on Linux/macOS)
                import os
                import subprocess
                import tempfile

                with tempfile.NamedTemporaryFile(delete=False, suffix=".der") as f:
                    f.write(der)
                    tmp = f.name
                try:
                    pub = subprocess.check_output(
                        [
                            "openssl",
                            "x509",
                            "-pubkey",
                            "-noout",
                            "-inform",
                            "DER",
                            "-in",
                            tmp,
                        ],
                        stderr=subprocess.DEVNULL,
                    )
                    dgst = subprocess.check_output(
                        ["openssl", "pkey", "-pubin", "-outform", "DER"],
                        input=pub,
                        stderr=subprocess.DEVNULL,
                    )
                    return hashlib.sha256(dgst).hexdigest()
                finally:
                    os.unlink(tmp)
    except Exception:
        return None


def tcp_reachable(addr: str, port: int) -> tuple[bool, str]:
    try:
        with socket.create_connection((addr, port), timeout=TIMEOUT):
            return True, "ok"
    except socket.timeout:
        return False, "timeout"
    except ConnectionRefusedError:
        return False, "connection refused"
    except OSError as e:
        return False, str(e)


def fetch_well_known() -> tuple[Optional[dict], Optional[str]]:
    """Returns (parsed_json, error_string)."""
    try:
        req = urllib.request.Request(
            WELL_KNOWN_URL, headers={"Cache-Control": "no-cache"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)


def verify_ed25519(data: dict, sig_field: str) -> tuple[bool, str]:
    """Verify the Ed25519 signature over canonical JSON (signature field excluded)."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return (
            False,
            "cryptography library not installed — run: pip install cryptography",
        )

    if not sig_field.startswith("ed25519:"):
        return False, f"unexpected signature format: {sig_field[:20]}"

    b64url = sig_field[len("ed25519:") :]
    # base64url → base64
    pad = 4 - len(b64url) % 4
    b64 = b64url.replace("-", "+").replace("_", "/") + ("=" * (pad % 4))
    try:
        sig_bytes = __import__("base64").b64decode(b64)
    except Exception as e:
        return False, f"base64 decode error: {e}"

    # Canonical form: remove signature, sort keys, compact
    payload = {k: v for k, v in data.items() if k != "signature"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    pub_bytes = bytes.fromhex(SIGNING_PUBLIC_KEY_HEX)
    pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
    try:
        pub_key.verify(sig_bytes, canonical)
        return True, "valid"
    except InvalidSignature:
        return False, "INVALID — signature does not match payload"
    except Exception as e:
        return False, str(e)


# ── Test suites ────────────────────────────────────────────────────────────────


def check_tcp_reachability() -> Suite:
    suite = Suite("TCP reachability")
    targets = [(r["addr"], r["port"], r["id"]) for r in RELAYS] + [
        (MAIN_SERVER["addr"], MAIN_SERVER["port"], "main-server")
    ]
    for addr, port, label in targets:
        ok, detail = tcp_reachable(addr, port)
        suite.add(f"{label} {addr}:{port}", ok, detail)
    return suite


def check_spki_pins() -> Suite:
    suite = Suite("TLS SPKI pins")
    for relay in RELAYS:
        label = relay["id"]
        addr, port, sni = relay["addr"], relay["port"], relay["sni"]
        live_spki = fetch_spki(addr, port, sni)

        if live_spki is None:
            suite.add(f"{label} — live SPKI fetch", False, "TLS connect failed")
            continue

        suite.add(f"{label} — live SPKI fetch", True, live_spki[:16] + "…")

        hardcoded = relay.get("spki_hardcoded")
        if hardcoded:
            match = live_spki == hardcoded
            suite.add(
                f"{label} — SPKI matches hardcoded pin",
                match,
                f"live={live_spki[:16]}… expected={hardcoded[:16]}…"
                if not match
                else "match",
            )
    return suite


def check_well_known(live_spkis: dict) -> Suite:
    suite = Suite(".well-known/construct-server")

    config, err = fetch_well_known()
    if not suite.add("fetch", config is not None, err or "ok"):
        return suite  # nothing more to check

    # Ed25519 signature
    sig = config.get("signature", "")
    if sig:
        ok, detail = verify_ed25519(config, sig)
        suite.add("Ed25519 signature valid", ok, detail)
    else:
        suite.add("Ed25519 signature present", False, "missing 'signature' field")

    # signed_at staleness (warn if > 48h)
    signed_at_str = config.get("signed_at", "")
    if signed_at_str:
        try:
            signed_at = datetime.fromisoformat(signed_at_str.replace("Z", "+00:00"))
            age_h = (datetime.now(timezone.utc) - signed_at).total_seconds() / 3600
            stale = age_h > 48
            suite.add(
                "signed_at freshness",
                True,
                f"{age_h:.0f}h ago",
                warning=stale,
            )
        except ValueError:
            suite.add("signed_at parse", False, f"invalid format: {signed_at_str}")

    # SPKI entries match live relays
    relays_in_config = config.get("veil", {}).get("relays", [])
    if not relays_in_config:
        suite.add("relays array present", False, "veil.relays is empty or missing")
    else:
        suite.add("relays array present", True, f"{len(relays_in_config)} relay(s)")
        for r in relays_in_config:
            rid = r.get("id", "?")
            config_spki = r.get("spki_sha256", "")
            live_spki = live_spkis.get(rid)
            if live_spki and config_spki:
                match = config_spki == live_spki
                suite.add(
                    f"relay {rid} — config SPKI matches live",
                    match,
                    f"config={config_spki[:16]}… live={live_spki[:16]}…"
                    if not match
                    else "match",
                )
            elif not config_spki:
                suite.add(
                    f"relay {rid} — spki_sha256 present", False, "missing spki_sha256"
                )

    return suite


# ── Output ─────────────────────────────────────────────────────────────────────

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "
SKIP = "  "


def print_suite(suite: Suite):
    status = PASS if suite.passed else FAIL
    print(f"\n{status} {suite.name}")
    for c in suite.checks:
        icon = PASS if c.passed else FAIL
        if c.passed and c.warning:
            icon = WARN
        detail = f"  ({c.detail})" if c.detail else ""
        print(f"  {icon}  {c.name}{detail}")


def print_json_result(suites: list[Suite]):
    out = {"passed": all(s.passed for s in suites), "suites": []}
    for s in suites:
        out["suites"].append(
            {
                "name": s.name,
                "passed": s.passed,
                "checks": [
                    {"name": c.name, "passed": c.passed, "detail": c.detail}
                    for c in s.checks
                ],
            }
        )
    print(json.dumps(out, indent=2))


# ── Main ───────────────────────────────────────────────────────────────────────


def main():
    ci_mode = "--ci" in sys.argv
    json_mode = "--json" in sys.argv

    if not json_mode:
        print(
            f"Construct VEIL smoke test — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        print(f"   Well-known: {WELL_KNOWN_URL}")

    # Collect live SPKIs first (reused across suites)
    live_spkis: dict[str, str] = {}
    for relay in RELAYS:
        spki = fetch_spki(relay["addr"], relay["port"], relay["sni"])
        if spki:
            live_spkis[relay["id"]] = spki

    suites = [
        check_tcp_reachability(),
        check_spki_pins(),
        check_well_known(live_spkis),
    ]

    if json_mode:
        print_json_result(suites)
    else:
        for suite in suites:
            print_suite(suite)

        total_checks = sum(len(s.checks) for s in suites)
        total_failed = sum(s.failed_count for s in suites)
        all_passed = all(s.passed for s in suites)

        print(f"\n{'─' * 50}")
        if all_passed:
            print(f"✅  All {total_checks} checks passed.")
        else:
            print(f"❌  {total_failed} / {total_checks} checks FAILED.")

    if ci_mode and not all(s.passed for s in suites):
        sys.exit(1)


if __name__ == "__main__":
    main()
