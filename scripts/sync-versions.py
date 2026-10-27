#!/usr/bin/env python3
"""Recompute every cache marker on the site. Run after editing copy or styles.

Three markers must move whenever their content does, or browsers keep serving
what they already have:

  I18N_CACHE_VER in site.js   the sessionStorage locale dictionary
  styles.css?v= on each page  the stylesheet
  site.js?v= on each page     the script that carries the first marker
  effects.css?v= on index     the front page's CRT sheet
  theme.js?v= on each page    the theme switch in <head>
  lang-redirect.js?v=         the first-visit language redirect in <head>

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
# add.html and contact.html are reached by following an invite, not from the
# nav, which is how they sat outside this list long enough to freeze at
# `?v=20260812-lang` while the stylesheet moved on underneath them.
PAGES = ("index.html", "faq.html", "privacy.html", "technical.html",
         "roadmap.html", "add.html", "contact.html")
LANGS = ("en", "ru", "ja", "hy", "fr", "uk", "tr")

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
# Its own hash: this used to be css_ver, so an edit to effects.css alone left
# the marker where it was and browsers on the cached sheet.
effects_ver = h10((ROOT / "effects.css").read_bytes())
theme_ver = h10((ROOT / "theme.js").read_bytes())
js_ver = h10((ROOT / "site.js").read_bytes())
redirect_ver = h10((ROOT / "lang-redirect.js").read_bytes())

for name in PAGES:
    page = ROOT / name
    before = page.read_text(encoding="utf-8")
    after = re.sub(r'styles\.css\?v=[0-9a-z-]+', f"styles.css?v={css_ver}", before)
    after = re.sub(r'effects\.css\?v=[0-9a-z-]+', f"effects.css?v={effects_ver}", after)
    after = re.sub(r'src="/site\.js(?:\?v=[0-9a-z]+)?"', f'src="/site.js?v={js_ver}"', after)
    after = re.sub(r'src="/theme\.js(?:\?v=[0-9a-z]+)?"', f'src="/theme.js?v={theme_ver}"', after)
    after = re.sub(r'src="/lang-redirect\.js(?:\?v=[0-9a-z]+)?"',
                   f'src="/lang-redirect.js?v={redirect_ver}"', after)
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
