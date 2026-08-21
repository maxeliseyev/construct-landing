#!/usr/bin/env python3
"""Take the Russian copy out to markdown for editing, and put it back.

    python3 scripts/ru-review.py export    # i18n/ru.json  -> i18n/review/*.md
    python3 scripts/ru-review.py import    # i18n/review/*.md -> i18n/ru.json
    python3 scripts/ru-review.py check     # is the markdown in sync with the JSON?

Editing Russian prose inside a 390-key JSON file means counting quotes and
escapes around every sentence, which is a poor way to spend attention that
should be going on the wording. This moves the words into one markdown file per
section, with the English above each one for reference, and moves them back.

The round trip is verified, not assumed: `export` re-parses what it just wrote
and refuses to leave a file behind that would not read back byte-identical. So
an edit is the only thing that can change a value.

What the markdown carries:

    ## faq.contacts.p3  ·  plain text
    > How do I message someone?
    Как написать человеку?

The heading is the key — do not change it, it is what the site looks the string
up by. The `>` line is the English original; it is ignored on import, so
correcting it there does nothing. Everything after it, up to the next heading,
is the Russian, and that is the part to edit.

`plain text` vs `HTML allowed` is not advice. A key written with `data-i18n`
goes into the page through textContent, so a tag typed there renders as
literal `<strong>` on the site; check-i18n fails the push for exactly this.
Only the keys marked `HTML allowed` are read as markup.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REVIEW = ROOT / "i18n/review"
HEADING = re.compile(r"^##\s+([A-Za-z0-9_.\-]+)\s*(?:·.*)?$")

# Written by scripts/stamp-privacy.py from the policy's own hash, not by a
# person. Editing it here would be silently reverted the next time the policy
# text moves, so it is exported read-only and refused on import.
GENERATED = {"privacy.privacy-policy.p2"}


def load(lang: str) -> dict[str, str]:
    return json.loads((ROOT / f"i18n/{lang}.json").read_text(encoding="utf-8"))


def html_keys() -> set[str]:
    """Keys the markup applies with innerHTML; everything else is textContent."""
    keys: set[str] = set()
    for page in ROOT.glob("*.html"):
        keys.update(re.findall(r'data-i18n-html="([^"]+)"', page.read_text(encoding="utf-8")))
    return keys


def section_of(key: str) -> str:
    return key.split(".")[0]


def render(section: str, keys: list[str], ru: dict, en: dict, html: set[str]) -> str:
    out = [
        f"# {section}",
        "",
        "Edit the Russian only — the `##` heading is the key the site looks the",
        "string up by, and the `>` line is the English original for reference.",
        "When you are done: `python3 scripts/ru-review.py import`",
        "",
    ]
    for key in keys:
        if key in GENERATED:
            kind = "GENERATED — do not edit, stamp-privacy.py owns this line"
        else:
            kind = "HTML allowed" if key in html else "plain text"
        out += [f"## {key}  ·  {kind}", ""]
        english = en.get(key, "")
        for line in english.split("\n"):
            out.append(f"> {line}")
        out += ["", ru[key], ""]
    return "\n".join(out).rstrip() + "\n"


def parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if key is not None:
            values[key] = "\n".join(buf).strip("\n").strip()

    for line in text.split("\n"):
        match = HEADING.match(line)
        if match:
            flush()
            key, buf = match.group(1), []
            continue
        if key is None or line.startswith(">"):
            continue
        buf.append(line)
    flush()
    return values


def export() -> int:
    ru, en, html = load("ru"), load("en"), html_keys()
    REVIEW.mkdir(parents=True, exist_ok=True)

    sections: dict[str, list[str]] = {}
    for key in sorted(ru):
        sections.setdefault(section_of(key), []).append(key)

    written, recovered = [], {}
    for section, keys in sections.items():
        text = render(section, keys, ru, en, html)
        recovered.update(parse(text))
        path = REVIEW / f"{section}.md"
        path.write_text(text, encoding="utf-8")
        written.append((path, len(keys)))

    # Refuse to leave behind a file that would not read back unchanged.
    broken = [k for k in ru if recovered.get(k) != ru[k]]
    if broken:
        for path, _ in written:
            path.unlink()
        print(f"ABORTED: {len(broken)} value(s) would not survive the round trip, "
              f"e.g. {broken[:3]}")
        print("No files written. The markdown format cannot represent those values.")
        return 1

    for path, count in written:
        print(f"  {path.relative_to(ROOT)}  ({count} keys)")
    print(f"\n{len(ru)} keys exported, round trip verified.")
    return 0


def collect() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in sorted(REVIEW.glob("*.md")):
        values.update(parse(path.read_text(encoding="utf-8")))
    return values


def import_() -> int:
    if not REVIEW.exists():
        print(f"No {REVIEW.relative_to(ROOT)} — run `export` first.")
        return 1

    ru, edited = load("ru"), collect()
    en = load("en")

    unknown = sorted(set(edited) - set(en))
    missing = sorted(set(ru) - set(edited))
    if unknown:
        print(f"FAIL: {len(unknown)} key(s) in the markdown are not in en.json — a "
              f"heading was renamed or invented: {unknown[:5]}")
        return 1
    if missing:
        print(f"FAIL: {len(missing)} key(s) have no heading in the markdown — a "
              f"section was deleted: {missing[:5]}")
        return 1

    empty = [k for k, v in edited.items() if not v.strip()]
    if empty:
        print(f"FAIL: {len(empty)} key(s) left empty: {empty[:5]}")
        return 1

    touched_generated = sorted(k for k in GENERATED
                               if k in edited and edited[k] != ru.get(k))
    if touched_generated:
        print(f"FAIL: {touched_generated} is generated by scripts/stamp-privacy.py "
              f"and would be overwritten the next time the policy text changes.")
        print("Change the date there, or leave it alone; nothing else was imported.")
        return 1

    changed = {k for k in edited if edited[k] != ru[k]}
    if not changed:
        print("No changes.")
        return 0

    ru.update(edited)
    (ROOT / "i18n/ru.json").write_text(
        json.dumps(ru, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    for key in sorted(changed):
        print(f"  {key}")
    print(f"\n{len(changed)} value(s) updated in i18n/ru.json.")
    print("Now run: python3 scripts/sync-versions.py && python3 scripts/check-i18n.py")
    return 0


def check() -> int:
    if not REVIEW.exists():
        print("no review files")
        return 0
    ru, edited = load("ru"), collect()
    drift = {k for k in edited if k in ru and edited[k] != ru[k]}
    if drift:
        print(f"{len(drift)} edited value(s) not yet imported, e.g. {sorted(drift)[:3]}")
        return 1
    print("review markdown matches i18n/ru.json")
    return 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "export":
        raise SystemExit(export())
    if command == "import":
        raise SystemExit(import_())
    if command == "check":
        raise SystemExit(check())
    raise SystemExit(__doc__)
