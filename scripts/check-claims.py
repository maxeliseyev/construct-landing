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
executed = 0


def read(path: pathlib.Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def site_copy() -> str:
    """Every published string, in every locale, plus the pages themselves.

    This read en.json alone for its first month, which made it a checker for the
    *translation*. Russian is the language the copy is written in — the English
    and Japanese are derived from it — so scanning only English inspected the
    downstream copy and trusted the source. A claim corrected in en.json while
    ru.json kept the old sentence passed green, and a claim only ever made in
    Russian was never read at all.

    Locale values are joined with a newline, not a space: a sentence ending one
    string and a sentence starting the next must not fuse into a phrase that
    matches a pattern neither of them contains.
    """
    parts = []
    for lang in ("en", "ru", "ja"):
        raw = read(SITE / f"i18n/{lang}.json")
        if raw:
            parts.append("\n".join(json.loads(raw).values()))
    # add.html and contact.html carry their copy inline rather than through the
    # locale files, so nothing here saw them until they were named. They make
    # the same claims about invites — single use, twelve hours — that the FAQ
    # makes, and a claim is no less published for being on a page you reach only
    # by following a link.
    for page in ("index.html", "faq.html", "privacy.html", "crypto.html",
                 "add.html", "contact.html"):
        t = read(SITE / page)
        if t:
            parts.append(t)
    return "\n".join(parts)


def check(name: str, ok: bool | None, detail: str) -> None:
    global executed
    if ok is None:
        skipped.append(f"SKIP {name}: {detail}")
        return
    executed += 1
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

# This check used to read `unwrap_or(300)` / `(60..=3600)` in invite_core.rs and
# reported green while the site said five minutes and the apps had moved to twelve
# hours. Those two numbers belong to `generate_invite` — a server-issued-token RPC
# with no caller — not to the signed dynamic invite the site is describing. A check
# pinned to the wrong constant is worse than none: it answers the question.
#
# The TTL a user experiences lives in two repositories, and this script is the only
# place that has both checked out, so it is the only place the two can be compared.

INVITE_TTL_SECONDS = None
_ttl_sources: dict[str, int | None] = {}

if IOS.exists():
    t = read(IOS / "ConstructMessenger/Utilities/Constants.swift")
    m = t and re.search(r"ttlSeconds:\s*TimeInterval\s*=\s*([\d_]+)", t)
    _ttl_sources["ios"] = int(m.group(1).replace("_", "")) if m else None
if SERVER.exists():
    t = read(SERVER / "crates/crypto-agility/src/invites.rs")
    m = t and re.search(r"INVITE_TTL_SECONDS:\s*i64\s*=\s*([\d_]+)", t)
    _ttl_sources["server"] = int(m.group(1).replace("_", "")) if m else None

if len(_ttl_sources) == 2:
    ios_ttl, server_ttl = _ttl_sources["ios"], _ttl_sources["server"]
    check(
        "invite-ttl-client-server-agree", None if None in (ios_ttl, server_ttl)
        else ios_ttl == server_ttl,
        f"iOS InviteConfig.ttlSeconds={ios_ttl} but construct-server "
        f"INVITE_TTL_SECONDS={server_ttl}. The server checks expiry first, so the "
        "shorter one wins and the sender's app shows a link it believes is live.",
    )
    if ios_ttl == server_ttl:
        INVITE_TTL_SECONDS = ios_ttl
else:
    check("invite-ttl-client-server-agree", None, "both app repos needed to compare")

# What the copy says, against what the code does. Add a spelling here when the copy
# changes — the point is that the sentence and the constant cannot drift apart
# silently, not that any particular wording is blessed.
_SPELLED_TTL = {
    r"five minutes|пять минут|5分": 300,
    r"twelve hours|двенадцать часов|12時間": 43_200,
}
for pattern, seconds in _SPELLED_TTL.items():
    if copy_says(pattern):
        check(
            f"invite-ttl-copy-{seconds}s", None if INVITE_TTL_SECONDS is None
            else INVITE_TTL_SECONDS == seconds,
            f"The site spells the invite lifetime as {seconds} s, the apps use "
            f"{INVITE_TTL_SECONDS} s.",
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

# ── The two identity spaces ──────────────────────────────────────────────────
#
# The privacy policy said the User ID was "derived mathematically from your
# device's cryptographic Identity Key". It is not: the server inserts
# gen_random_uuid(). What IS a hash of the identity key is the *Device ID*
# (hex(SHA256(pk)[0..16])), a different identifier in a different space —
# exactly the confusion AGENTS.md flags as CRITICAL, here leaking into a legal
# document. It also had the privacy argument backwards: a derived id is
# computable by anyone holding the public key, a random UUID is not.
#
# Both halves are pinned, because either drifting alone re-opens the claim.

repo_claim(
    "user-id-is-server-random",
    SERVER, "crates/construct-db/src/lib.rs",
    r"INSERT INTO users\s*\([^)]*\bid\b[^)]*\)\s*VALUES\s*\(\s*gen_random_uuid\(\)",
    present=True,
    detail="users.id is no longer gen_random_uuid(). The policy says the User ID is a "
           "random UUID the server generates and is not derived from your keys — "
           "re-read the INSERT before touching privacy.s2_1.li3.",
)

repo_claim(
    "device-id-is-hash-of-identity-key",
    CORE, "src/device_id.rs",
    r"fn derive_device_id\(identity_public_key: &\[u8\]\)",
    present=True,
    detail="derive_device_id() changed shape. The policy says the Device ID is a hash "
           "of the public Identity Key (privacy.s2_1.li3b) — verify before shipping.",
)

# The first version of this check matched only "derived|выведен|導出", because that
# is the wording of the one instance I had found. It passed green while a second
# copy of the same false claim sat in privacy.s8_1.p2 saying "cryptographic hash"
# — a checker written against the sample instead of against the claim. The claim
# is "the User ID is a function of something", however that is phrased.
if copy_says(r"user\s*id"):
    check(
        "user-id-not-claimed-derived",
        not copy_says(
            # The gap must not cross a sentence end OR a string boundary: strings are
            # concatenated to form the corpus, and "[^.!?]" happily matched the
            # newline between them — fusing the Japanese User ID line to the Device
            # ID line that follows it, which legitimately says "hash". Japanese ends
            # sentences with "。", so that has to stop the gap too.
            r"user\s*id[^.!?。\n]{0,160}"
            r"(derived|derive|выведен|производн|"
            r"(cryptographic |криптографическ\w+ )?(hash|хеш|хэш|ハッシュ)|"
            # Japanese negates after the verb, so the stem alone matches the
            # sentence that says the opposite: 導出されておらず = "is NOT derived".
            r"導出(?![^。]{0,14}(おらず|いません|いない|ありません|ず))|"
            r"from your .{0,30}key|из .{0,30}ключа)"
        ),
        "The copy says the User ID is a hash of, or derived from, something. It is "
        "gen_random_uuid() on the server — a value with no preimage. Being a function "
        "of a key would be WORSE here: anyone holding that public key could recompute "
        "it. Derivation belongs to the Device ID (privacy.s2_1.li3b), not the User ID.",
    )

# ── Calls are audio-only ─────────────────────────────────────────────────────
#
# The privacy policy had a section headed "Voice and Video Calls" and described
# encrypting "call media (audio/video)". Video was never started: CallsFeature
# says isVideoEnabled = false, every call site passes hasVideo: false, and there
# is not one VideoTrack in Services/Calls. The signalling wiring exists, which is
# how the claim got written — wiring is not a feature.

repo_claim(
    "video-calls-still-off",
    IOS, "ConstructMessenger/Services/Calls/CallsFeature.swift",
    r"isVideoEnabled: Bool \{ false \}",
    present=True,
    detail="isVideoEnabled is no longer hard-false. If video calling shipped, the "
           "privacy policy (privacy.s2_7.*) and the roadmap have to stop saying it "
           "is not implemented.",
)

# A blacklist of the phrasings that actually shipped on this site, not a general
# "is video mentioned" test. The first attempt at this check was vacuous: it
# accepted the copy if the word "planned" appeared ANYWHERE, and the roadmap
# always contains it, so the assertion was true by construction. Mutation caught
# it — restoring the old "Voice and Video Calls" heading did not turn it red.
#
# NOT COVERED, deliberately: a novel phrasing ("we support camera calls") passes
# this. The load-bearing guard is video-calls-still-off above, which reads the
# flag in the app; this one only stops the exact sentences from coming back.
VIDEO_SHIPPED = (
    r"voice(?: |/|, | and )*video calls? (?:are|is)\b|"
    r"call media \(audio/video\)|voice/video call|audio/video\b|"
    r"voice and video calls|"
    r"аудио-? и видеозвонк|видеозвонки защищ|аудио/видеозвонк|"
    r"音声・ビデオ通話|音声/ビデオ通話"
)

if copy_says(r"video call|видеозвон|ビデオ通話"):
    check(
        "video-calls-not-claimed-shipped",
        not copy_says(VIDEO_SHIPPED),
        "The copy states video calls as a working feature. CallsFeature."
        "isVideoEnabled is false, every call site passes hasVideo: false, and there "
        "is no VideoTrack anywhere in Services/Calls. The signalling is wired, which "
        "is how this got written the first time — wiring is not a feature.",
    )

# ── Social recovery ──────────────────────────────────────────────────────────
#
# Two different features share a vocabulary, and only one of them exists.
#
#   seed phrase / backup export   SHIPPED — Settings ▸ Account ▸ Export Backup
#                                 (ExportBackupView generates a mnemonic and
#                                 writes a backup file). faq.registration.p7 may
#                                 say so.
#   social recovery, SLIP-39      NOT BUILT — access reassembled from shards
#                                 handed to people you chose. Roadmap only.
#
# The home page described the second as design intent. It was not a false claim
# — it carried "(in development — not shipped)" — and it was removed as an
# editorial call: the site does not describe what does not exist. This check
# keeps the distinction from eroding into "we have social recovery".

# Checked per string, not across the corpus. Asking "does 'in progress' appear
# anywhere?" is how the video check came out tautological — the roadmap always
# contains it, so the answer is always yes and the assertion means nothing. The
# marker has to be in the SAME string as the mention.
SOCIAL = r"SLIP-?39|social recovery|социальн\w+ восстановлен"
PLANNED = r"in progress|в работе|planned|roadmap|進行中|not shipped|не выпущено"

stray = [ln for ln in COPY.splitlines()
         if re.search(SOCIAL, ln, re.I) and not re.search(PLANNED, ln, re.I)]
if re.search(SOCIAL, COPY, re.I):
    check(
        "social-recovery-marked-unbuilt",
        not stray,
        "Social recovery / SLIP-39 is described without a planned marker in the same "
        "sentence. Sharded recovery is NOT built. What ships is a personal seed "
        "phrase (Settings ▸ Account ▸ Export Backup, ExportBackupView) — a different "
        "feature that happens to share the vocabulary. First offending line:\n       "
        + (stray[0][:160] if stray else ""),
    )

# ── Roadmap honesty ──────────────────────────────────────────────────────────

if copy_says(r"\bfederat"):
    check(
        "federation-marked-planned",
        copy_says(r"federation.{0,40}(planned|roadmap|2027)|(planned|roadmap).{0,40}federat"),
        "Federation is mentioned without being marked planned anywhere. It is not shipped.",
    )

# ── The READMEs say it too ───────────────────────────────────────────────────
#
# Everything above reads the *site*. That is where this file started, and it is
# why an external review on 2026-08-18 found six live contradictions that the
# checker had passed green a day earlier: the site said video is not
# implemented, and construct-messenger/README.md said "[x] Voice/video calls",
# three feet from a checker that already knew isVideoEnabled was false.
#
# A reader who is deciding whether to trust the cryptography does not respect
# the boundary between our website and our repositories. Neither should this.
#
# Read the READMEs as one more corpus and re-apply the claims that have already
# gone wrong once. Missing repos SKIP, they do not pass — same rule as
# repo_claim, for the same reason.

DOCS = (
    ("construct-core/README.md", CORE / "README.md"),
    ("construct-messenger/README.md", IOS / "README.md"),
    ("construct-server/README.md", SERVER / "README.md"),
)


def doc_lines(pattern: str, unless: str | None = None) -> list[str] | None:
    """Lines across every README matching `pattern`, or None if none could be read.

    `unless` exempts a line that carries its own correction. Without it the video
    check flagged the very line that says video is *not* implemented — the same
    tautology the social-recovery check above was written twice to avoid. A
    pattern that also matches the fix cannot tell you the fix is in place.
    """
    hits, read_any = [], False
    for label, path in DOCS:
        text = read(path)
        if text is None:
            continue
        read_any = True
        hits += [f"{label}: {ln.strip()[:150]}" for ln in text.splitlines()
                 if re.search(pattern, ln, re.I)
                 and not (unless and re.search(unless, ln, re.I))]
    return hits if read_any else None


def docs_must_not(name: str, pattern: str, detail: str,
                  unless: str | None = None) -> None:
    hits = doc_lines(pattern, unless)
    if hits is None:
        check(name, None, "no sibling README was readable")
        return
    check(name, not hits, detail + ("\n       " + "\n       ".join(hits[:3]) if hits else ""))


# The word means "an auditor looked at this". No auditor has. It sat in the core
# and iOS READMEs inside "the same audited code", where it was doing the work of
# "shared" — one implementation, not five — and read as a credential we do not
# hold. Re-earn it by publishing a report, not by re-typing it.
docs_must_not(
    "readme-does-not-claim-audited",
    r"\baudited\b",
    "A README calls our own code audited. No external security audit has been "
    "done — the site says so on the roadmap. Use 'shared' when the point is one "
    "implementation across platforms.",
)

# Guarded by video-calls-still-off above, which pins isVideoEnabled == false.
docs_must_not(
    "readme-does-not-ship-video-calls",
    r"voice ?/ ?video calls?|voice and video calls|\[x\].*video",
    "A README lists video calling as done. CallsFeature.isVideoEnabled is false "
    "and the privacy policy says video is not implemented.",
    unless=r"video is not implemented|no video|video: planned",
)

# construct-core/README.md is the authority: "not yet activated on the wire".
# Anything that describes the hybrid signature in plain present tense contradicts
# the one document that tracks it.
core_readme = read(CORE / "README.md")
if core_readme and re.search(r"not yet activated on the wire", core_readme, re.I):
    stray_pq = [ln for ln in COPY.splitlines()
                if re.search(r"ML-DSA", ln, re.I)
                and not re.search(r"not yet active|not active|implemented|in progress|"
                                  r"пока не задействован|реализован|planned|進行中|まだ", ln, re.I)]
    check(
        "ml-dsa-not-claimed-active",
        not stray_pq,
        "The copy describes ML-DSA signatures as in use. construct-core/README.md "
        "says they are 'not yet activated on the wire' — implemented is not active. "
        "First offending line:\n       " + (stray_pq[0][:160] if stray_pq else ""),
    )

# Multi-device is the case where the code is finished and the feature is not.
# Linking and SENDER_SYNC are implemented and unit-tested; no stand run has yet
# carried a copy through to a second device's transcript, so nothing has been
# seen working on hardware. construct-messenger/README.md is the authority and
# keeps it under "In progress / planned" until a run does.
#
# Deriving this from the presence of the code would assert the wrong thing —
# the code is there. What is missing is evidence, and the README is where we
# record having it.
ios_readme = read(IOS / "README.md")
if ios_readme:
    planned = ios_readme.split("### In progress / planned")[-1]
    if re.search(r"multi-?device", planned, re.I):
        # A question is not a claim. The FAQ heading "Поддерживается ли несколько
        # устройств?" cannot carry a planned marker — its answer does, in the next
        # string — and flagging it would push the marker into the question, which
        # is how FAQ headings stop reading like questions.
        stray_md = [ln for ln in COPY.splitlines()
                    if re.search(r"multi-?device|мультидевайс|нескольк\w+ устройств|複数.{0,4}デバイス", ln, re.I)
                    and not ln.rstrip().endswith(("?", "？"))
                    # "control paths (heartbeats, multi-device, session control) stay
                    # identified by design" names which internal path carries a sender.
                    # It is not an offer of the feature, and rewriting it to add a
                    # planned marker would make the sentence say something false about
                    # the protocol.
                    and not re.search(r"session control|heartbeat|control-пут|control path", ln, re.I)
                    and not re.search(r"in development|in progress|planned|roadmap|not yet|do not exist|"
                                      r"в разработк|планир|пока нет|開発中|まだ|進行中", ln, re.I)]
        check(
            "multi-device-not-claimed-working",
            not stray_md,
            "The copy presents multi-device as working. It is implemented but has "
            "never been confirmed on hardware — construct-messenger/README.md keeps "
            "it under 'In progress / planned'. Move it there first, then say so here. "
            "First offending line:\n       " + (stray_md[0][:160] if stray_md else ""),
        )

# Contact edges ARE stored — as HMAC-SHA256 of both account ids
# (037_contact_links.sql). "No social-graph metadata at rest" was false while
# that migration existed, and it is the kind of false that a reader checks in
# five minutes against a public schema.
if (SERVER / "shared/migrations/037_contact_links.sql").exists():
    docs_must_not(
        "no-absolute-social-graph-denial",
        r"no social.graph metadata at rest|does not track who messages whom",
        "A README denies storing the social graph. contact_links stores an edge "
        "per contact — blinded (HMAC of both ids), which defeats a database leak, "
        "but the server holds the key. Say that instead of denying the row.",
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

# Without the sibling repos every repo_claim SKIPs and this printed "OK: every
# checked claim still matches the code" with exit 0 — true, vacuously, because
# nothing was checked. That is the reassuring shape this whole file exists to
# avoid, and it is the shape that let SessionQueueWiringTests read all-zeros for
# five weeks. "Could not check" is not "checked and fine", so it is not green.
#
# --allow-missing-repos is for the case where you know and accept it (a CI job
# that only lints the copy). It still prints what went unverified.
if skipped and "--allow-missing-repos" not in sys.argv:
    print(f"{len(skipped)} claim(s) COULD NOT BE CHECKED — the code they describe was not\n"
          "readable. This is not a pass. Check out the sibling repos beside this one, or\n"
          "pass --allow-missing-repos if you are deliberately linting copy alone.")
    sys.exit(2)

print(f"OK: {executed} claim(s) checked against the code"
      + (f"; {len(skipped)} skipped." if skipped else "."))
