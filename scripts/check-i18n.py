#!/usr/bin/env python3
"""Parity check for JSON i18n.

Usage (repo root):
  python3 scripts/check-i18n.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("en", "ru", "ja")
HTML_FILES = ("index.html", "faq.html", "privacy.html")


def load_dict(lang: str) -> dict:
    path = ROOT / "i18n" / f"{lang}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def keys_in_html(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    keys = set()
    for attr in ("data-i18n", "data-i18n-html"):
        keys.update(re.findall(rf'{attr}="([^"]+)"', text))
    return keys


def main() -> int:
    dicts = {lang: load_dict(lang) for lang in LANGS}
    base = set(dicts["en"].keys())
    ok = True

    for lang in LANGS[1:]:
        other = set(dicts[lang].keys())
        missing = base - other
        extra = other - base
        if missing:
            ok = False
            print(f"FAIL {lang}: missing {len(missing)} keys, e.g. {sorted(missing)[:5]}")
        if extra:
            ok = False
            print(f"FAIL {lang}: extra {len(extra)} keys, e.g. {sorted(extra)[:5]}")

    used: set[str] = set()
    for name in HTML_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        keys = keys_in_html(path)
        used |= keys
        missing = keys - base
        if missing:
            ok = False
            print(f"FAIL {name}: {len(missing)} keys not in en.json: {sorted(missing)[:10]}")
        # leftover class-based locales
        for lang in LANGS:
            n = len(re.findall(rf'class="[^"]*\b{lang}\b', path.read_text(encoding="utf-8")))
            # lang-name / lang-code are fine; only bare locale class leftovers
            n_bare = len(re.findall(rf'class="{lang}"', path.read_text(encoding="utf-8")))
            if n_bare:
                ok = False
                print(f"FAIL {name}: still has class=\"{lang}\" ({n_bare})")

    unused = base - used - {k for k in base if k.endswith(".meta.title")}
    # meta.title is applied via page namespace, not data-i18n attr
    unused = {k for k in unused if not k.endswith(".meta.title")}
    if unused:
        print(f"WARN unused keys in en.json: {len(unused)} e.g. {sorted(unused)[:8]}")

    empty = [k for k, v in dicts["en"].items() if not str(v).strip()]
    if empty:
        ok = False
        print(f"FAIL empty en values: {empty[:5]}")

    if ok:
        print(f"OK: {len(base)} keys × {len(LANGS)} langs; {len(used)} HTML refs")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
