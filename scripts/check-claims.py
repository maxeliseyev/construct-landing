#!/usr/bin/env python3
"""Re-derive the site's factual claims from the sibling repositories.

Every claim below was wrong on the live site at some point, or is one sentence
away from becoming wrong. The audit that found them was a one-off; this is the
part that runs again.

Same idea as construct-messenger/scripts/check_privacy_manifest.sh: a document
maintained by hand drifts, so derive it instead of re-reading it.

    python3 scripts/check-claims.py          # exit 1 on any failure
    python3 scripts/check-claims.py -v       # show every check

NOT a test of the code — it does not care whether the code is *right*, only
whether the website still describes it accurately.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HOME = pathlib.Path.home() / "Code"
SITE = pathlib.Path(__file__).resolve().parent.parent

IOS = HOME / "construct-messenger"
CORE = HOME / "construct-core"
SERVER = HOME / "construct-server"

VERBOSE = "-v" in sys.argv
failures: list[str] = []
skipped: list[str] = []


def read(path: pathlib.Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def site_copy() -> str:
    """All public English copy: the i18n strings plus the pages without i18n."""
    parts = []
    en = read(SITE / "i18n/en.json")
    if en:
        parts.append(" ".join(json.loads(en).values()))
    for page in ("index.html", "faq.html", "privacy.html", "crypto.html"):
        t = read(SITE / page)
        if t:
            parts.append(t)
    return "\n".join(parts)


def check(name: str, ok: bool | None, detail: str) -> None:
    if ok is None:
        skipped.append(f"SKIP {name}: {detail}")
        return
    if ok:
        if VERBOSE:
            print(f"  ok   {name}")
        return
    failures.append(f"FAIL {name}\n       {detail}")


def repo_claim(name: str, repo: pathlib.Path, rel: str, pattern: str,
               present: bool, detail: str) -> None:
    """Assert `pattern` is (or is not) in a sibling repo file."""
    if not repo.exists():
        check(name, None, f"{repo.name} not checked out")
        return
    text = read(repo / rel)
    if text is None:
        check(name, False, f"{rel} is gone — the claim's evidence moved. {detail}")
        return
    found = re.search(pattern, text) is not None
    check(name, found is present, detail)


COPY = site_copy()


def copy_says(pattern: str) -> bool:
    return re.search(pattern, COPY, re.IGNORECASE) is not None


print("check-claims: re-deriving site claims from the code\n")

# ── Post-quantum ─────────────────────────────────────────────────────────────
#
# The site says PQXDH. What makes that true is the initiator encapsulating to
# the peer's Kyber prekey at session init — NOT the negotiated suite id. Reading
# the suite is what produced a wrong retraction on 2026-08-12: PQXDH is not
# suite-gated, so `negotiated_initiator_suite` returning CLASSIC says nothing
# about it. Pin the call, never the suite.

if copy_says(r"PQXDH"):
    repo_claim(
        "pqxdh-initiator", CORE, "src/orchestration/orchestrator.rs",
        r"encapsulate_and_defer", True,
        "The site claims PQXDH but the orchestrator no longer encapsulates to the "
        "peer's Kyber prekey. Either the path moved or PQXDH is gone.",
    )
    repo_claim(
        "pqxdh-responder", IOS, "ConstructMessenger/Services/Messaging/MessageRouter.swift",
        r"applyIncomingContribution", True,
        "No responder-side PQ contribution on iOS — a claimed PQXDH with no receiver.",
    )
    repo_claim(
        "pqxdh-prekeys-published", IOS, "ConstructMessenger/Views/Onboarding/RegistrationFlowView.swift",
        r"generateAndUploadKyberOtpks|commitKyberSPK", True,
        "Registration no longer publishes Kyber prekeys, so peers cannot encapsulate to us.",
    )

# The "message zero is classical" caveat is only worth printing while it is true.
if copy_says(r"first message.{0,80}classical|classical.{0,80}first message|0通目|нулевое сообщение"):
    repo_claim(
        "pq-deferred-after-msg0", IOS, "ConstructMessenger/Security/PQCKeyManager.swift",
        r"deferred until after msg0|msg0 uses classic-only", True,
        "The site says message zero is classical-only; the deferral it describes is gone.",
    )

if copy_says(r"ML-KEM-768"):
    repo_claim(
        "ml-kem-768", CORE, "src/crypto/suite_id.rs", r"ML-KEM-768", True,
        "ML-KEM-768 is claimed but not named in the core's suite definitions.",
    )

if copy_says(r"ML-DSA-65"):
    repo_claim(
        "ml-dsa-65", CORE, "src/crypto/suites/hybrid.rs", r"MlDsa65", True,
        "Hybrid ML-DSA-65 signatures are claimed; the core no longer implements them.",
    )

# ── Retired names ────────────────────────────────────────────────────────────

check(
    "no-construct-engine",
    not copy_says(r"ConstructEngine"),
    "ConstructEngine was deleted on 2026-07-28. The transport is construct-transport.",
)

# ── Identity and discovery ───────────────────────────────────────────────────

if copy_says(r"keyed hash|HMAC|ключев\w+ хеш|鍵付きハッシュ"):
    repo_claim(
        "username-is-hmac", SERVER, "crates/construct-crypto/src/username.rs",
        r"HmacSha256|Hmac<", True,
        "The site says usernames are stored as a keyed hash; the server no longer uses HMAC.",
    )

if copy_says(r"discovery is off|not discoverable|until you turn discovery on|пока вы не включите обнаружение|発見可能設定"):
    ok = None
    mig = SERVER / "shared/migrations/038_user_discoverable.sql"
    if SERVER.exists():
        t = read(mig)
        ok = bool(t and re.search(r"searchable\s+BOOLEAN\s+NOT NULL\s+DEFAULT\s+FALSE", t, re.I))
    check(
        "discovery-off-by-default", ok,
        "The site says an account is not discoverable by default; migration 038 no longer "
        "defaults `searchable` to FALSE. A later migration may have changed it — check.",
    )

# ── Invites ──────────────────────────────────────────────────────────────────

if copy_says(r"expire in minutes|codes expire|истекают|期限"):
    ok = None
    if SERVER.exists():
        t = read(SERVER / "identity-service/src/invite_core.rs")
        ok = bool(t and re.search(r"unwrap_or\(300\)", t) and re.search(r"\(60\.\.=3600\)", t))
    check(
        "invite-ttl-minutes", ok,
        "The site says invite codes expire in minutes; the TTL default/range in "
        "invite_core.rs no longer reads 300 s within 60–3600.",
    )

# ── Telemetry ────────────────────────────────────────────────────────────────

if copy_says(r"no third-party|Firebase|Crashlytics|Sentry"):
    ok = None
    resolved = IOS / "ConstructMessenger.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved"
    if IOS.exists():
        t = read(resolved)
        if t:
            trackers = ("firebase", "crashlytics", "sentry", "amplitude",
                        "segment", "mixpanel", "appsflyer", "adjust", "datadog")
            hit = [n for n in trackers if n in t.lower()]
            ok = not hit
            if hit:
                detail_extra = f" Found: {', '.join(hit)}."
            else:
                detail_extra = ""
    check(
        "no-tracker-sdks", ok,
        "The site says there are no third-party trackers; an analytics SDK is now a "
        "dependency." + (detail_extra if ok is False else ""),
    )

if copy_says(r"no diagnostic log|write no log|no logs? to disk|не пишут.{0,20}лог|ログ"):
    repo_claim(
        "release-writes-no-log", IOS, "ConstructMessenger/Utilities/LogCollector.swift",
        r"#if DEBUG \|\| INTERNAL_TOOLS", True,
        "The site says release builds write no log to disk; LogCollector's build gate changed.",
    )

# ── Anti-spam ────────────────────────────────────────────────────────────────

m = re.search(r"(\d+)\s*(?:messages\s*)?in\s*(\d+)\s*seconds", COPY, re.IGNORECASE)
if m:
    claimed_n, claimed_s = m.group(1), m.group(2)
    ok = None
    if IOS.exists():
        t = read(IOS / "ConstructMessenger/Services/AntiSpam/IncomingFloodGuard.swift")
        if t:
            n = re.search(r"burstThreshold\s*=\s*(\d+)", t)
            s = re.search(r"windowDuration:\s*TimeInterval\s*=\s*(\d+)", t)
            ok = bool(n and s and n.group(1) == claimed_n and s.group(1) == claimed_s)
    check(
        "flood-guard-numbers", ok,
        f"The site says ~{claimed_n} messages in {claimed_s} seconds; IncomingFloodGuard "
        "no longer uses those numbers.",
    )

if copy_says(r"Argon2id"):
    ok = None
    if SERVER.exists():
        hits = list(SERVER.rglob("*.rs"))
        ok = any("argon2" in (read(p) or "").lower() for p in hits[:4000])
    check("argon2id-pow", ok, "Argon2id proof-of-work is claimed but not found in the server.")

# ── Disclosure policy (decisions/public-copy-discloses-no-operational-status) ─
#
# The app is forbidden from showing these; the website is more public than the
# app. "construct-veil" as a repository name in the licensing list is identity,
# not a reachability coordinate, so it is allowed — the bare product name is not.

for label, term, why in (
    ("obfs4", r"\bobfs4\b", "names a specific obfuscation transport"),
    ("webtunnel", r"\bWebTunnel\b", "names a specific obfuscation transport"),
    ("veil-front", r"veil-front", "names the live front implementation"),
):
    check(
        f"no-mechanism-name-{label}",
        not copy_says(term),
        f"Public copy {why} ({term}). decisions/public-copy-discloses-no-operational-status: "
        "publish design, never operational status.",
    )

check(
    "no-bare-veil-name",
    not re.search(r"(?<!construct-)\bVEIL\b", COPY),
    "Public copy uses the internal codename VEIL. The app says 'censorship protection'; "
    "so should the site. `construct-veil` as a repo name is fine.",
)

check(
    "no-regional-status",
    not copy_says(r"throttled (by|in) .{0,30}(region|some regions|RU\b)"),
    "Public copy reports where circumvention currently does or does not work — that is a "
    "free effectiveness report for whoever is doing the blocking.",
)

# ── Donation addresses ───────────────────────────────────────────────────────
#
# DONATE.md is PGP-signed and says so: "If an address shown on the website ever
# differs from what is committed here, trust this file, not the page." Nothing
# enforced that. The QR images are the sharper risk — most people scan rather
# than read, and a swapped QR passes every text comparison.

donate = read(SITE / "DONATE.md")
if donate:
    want = {}
    m = re.search(r"^(4[0-9A-Za-z]{94,105})$", donate, re.M)
    if m:
        want["xmr"] = m.group(1)
    m = re.search(r"^(bc1[0-9a-z]{20,60})$", donate, re.M)
    if m:
        want["btc"] = m.group(1)

    for kind, addr in want.items():
        check(
            f"donate-{kind}-in-copy",
            addr in COPY,
            f"The {kind.upper()} address published on the site is not the one in the signed "
            f"DONATE.md. Verify with `gpg --verify DONATE.md.asc DONATE.md` before changing "
            f"anything.",
        )
        # Any address of that shape on the site must be *the* address.
        pat = r"4[0-9A-Za-z]{94,105}" if kind == "xmr" else r"bc1[0-9a-z]{20,60}"
        rogue = {a for a in re.findall(pat, COPY)} - {addr}
        check(
            f"donate-{kind}-no-rogue",
            not rogue,
            f"The site carries a second {kind.upper()}-shaped address: {sorted(rogue)[:1]}",
        )

    for kind, addr in want.items():
        f = SITE / f"qr-{kind}.svg"
        if not f.exists():
            continue
        try:
            sys.path.insert(0, str(SITE / "scripts"))
            from qr_modules import check as qr_check
            verdict = qr_check(str(f), addr)
        except Exception as e:                      # qrencode missing, parse change
            check(f"donate-{kind}-qr", None, f"could not verify: {e}")
            continue
        check(
            f"donate-{kind}-qr",
            verdict.startswith("MATCH"),
            f"qr-{kind}.svg does not encode the signed {kind.upper()} address ({verdict}). "
            f"A swapped QR is invisible to every text check on this page.",
        )

# ── Roadmap honesty ──────────────────────────────────────────────────────────

if copy_says(r"\bfederat"):
    check(
        "federation-marked-planned",
        copy_says(r"federation.{0,40}(planned|roadmap|2027)|(planned|roadmap).{0,40}federat"),
        "Federation is mentioned without being marked planned anywhere. It is not shipped.",
    )

# ── Report ───────────────────────────────────────────────────────────────────

for line in skipped:
    print(line)
if skipped:
    print()

if failures:
    for line in failures:
        print(line)
    print(f"\n{len(failures)} claim(s) no longer match the code.")
    sys.exit(1)

print("OK: every checked claim still matches the code.")
