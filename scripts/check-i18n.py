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

    # A `data-i18n` key is written with textContent, so an HTML entity in its value
    # is printed literally — Safari showed "2026 &nbsp;·&nbsp; Effective". Only
    # `data-i18n-html` keys go through innerHTML and may carry markup.
    #
    # This is the same defect the extractor had: it chose the attribute by looking
    # for a *tag* (`<[a-z]`), and an entity is not a tag. One carrier, two meanings.
    attr_of = {}
    for name in HTML_FILES:
        text = (ROOT / name).read_text(encoding="utf-8")
        for m in re.finditer(r'data-i18n(-html)?="([^"]+)"', text):
            attr_of[m.group(2)] = "html" if m.group(1) else "text"

    entity = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,31}|#\d+|#[xX][0-9a-fA-F]+);")
    literal = [
        f"{lang}:{k}"
        for lang, d in dicts.items()
        for k, v in d.items()
        if attr_of.get(k) == "text" and isinstance(v, str) and entity.search(v)
    ]
    if literal:
        ok = False
        print(f"FAIL {len(literal)} textContent value(s) contain HTML entities "
              f"— they will render literally: {literal[:5]}")

    markup = [
        f"{lang}:{k}"
        for lang, d in dicts.items()
        for k, v in d.items()
        if attr_of.get(k) == "text" and isinstance(v, str) and re.search(r"<[a-zA-Z/]", v)
    ]
    if markup:
        ok = False
        print(f"FAIL {len(markup)} textContent value(s) contain tags "
              f"— use data-i18n-html: {markup[:5]}")


    # The sessionStorage locale cache is keyed only by I18N_CACHE_VER in site.js.
    # If the dictionaries change and that constant does not, browsers keep serving
    # the old dictionary and every new key silently falls back to the English in
    # the markup — the switcher says RU over English text. It went wrong twice in
    # two days, the second time with a comment in site.js saying "bump this".
    # So it is derived, not remembered: the value must be the content hash.
    import hashlib
    h = hashlib.sha256()
    for lang in ("en", "ru", "ja"):
        h.update((ROOT / f"i18n/{lang}.json").read_bytes())
    want = h.hexdigest()[:10]
    site = (ROOT / "site.js").read_text(encoding="utf-8")
    m = re.search(r'var I18N_CACHE_VER = "([^"]*)";', site)
    if not m:
        ok = False
        print("FAIL site.js: I18N_CACHE_VER not found")
    elif m.group(1) != want:
        ok = False
        print(f'FAIL site.js: I18N_CACHE_VER is "{m.group(1)}", locales hash to "{want}" '
              f"— stale browser caches will serve the old dictionary. Set it to \"{want}\".")

    if ok:
        print(f"OK: {len(base)} keys × {len(LANGS)} langs; {len(used)} HTML refs")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
