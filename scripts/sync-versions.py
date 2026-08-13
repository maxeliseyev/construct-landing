#!/usr/bin/env python3
"""Recompute every cache marker on the site. Run after editing copy or styles.

Three markers must move whenever their content does, or browsers keep serving
what they already have:

  I18N_CACHE_VER in site.js   the sessionStorage locale dictionary
  styles.css?v= on each page  the stylesheet
  site.js?v= on each page     the script that carries the first marker

They are derived, not typed — `check-i18n.py` fails when any of them disagrees
with the file it stands for, and this script is what makes them agree. Order
matters: the locale key goes into site.js first, then site.js is hashed.

    python3 scripts/sync-versions.py          # fix them
    python3 scripts/sync-versions.py --check  # report only, exit 1 if stale
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ("index.html", "faq.html", "privacy.html", "technical.html", "roadmap.html")
LANGS = ("en", "ru", "ja")

check_only = "--check" in sys.argv
changed: list[str] = []


def h10(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


# 1. Locale dictionary → I18N_CACHE_VER
digest = hashlib.sha256()
for lang in LANGS:
    digest.update((ROOT / f"i18n/{lang}.json").read_bytes())
locale_ver = digest.hexdigest()[:10]

site = ROOT / "site.js"
text = site.read_text(encoding="utf-8")
current = re.search(r'var I18N_CACHE_VER = "([^"]*)";', text)
if not current:
    sys.exit("site.js: I18N_CACHE_VER not found")
if current.group(1) != locale_ver:
    changed.append(f"I18N_CACHE_VER {current.group(1)} -> {locale_ver}")
    if not check_only:
        site.write_text(
            re.sub(r'var I18N_CACHE_VER = "[^"]*";',
                   f'var I18N_CACHE_VER = "{locale_ver}";', text, count=1),
            encoding="utf-8")

# 2. Assets → ?v= on every page. site.js is hashed *after* the step above.
css_ver = h10((ROOT / "styles.css").read_bytes())
js_ver = h10((ROOT / "site.js").read_bytes())

for name in PAGES:
    page = ROOT / name
    before = page.read_text(encoding="utf-8")
    after = re.sub(r'styles\.css\?v=[0-9a-z-]+', f"styles.css?v={css_ver}", before)
    after = re.sub(r'effects\.css\?v=[0-9a-z-]+', f"effects.css?v={css_ver}", after)
    after = re.sub(r'src="/site\.js(?:\?v=[0-9a-z]+)?"', f'src="/site.js?v={js_ver}"', after)
    if after != before:
        changed.append(f"{name}: asset versions")
        if not check_only:
            page.write_text(after, encoding="utf-8")

if not changed:
    print("versions already in sync")
    sys.exit(0)

for line in changed:
    print(("stale: " if check_only else "updated: ") + line)
sys.exit(1 if check_only else 0)
