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
HTML_FILES = ("index.html", "faq.html", "privacy.html", "technical.html", "roadmap.html")


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


    # Nesting. Sections have been cut out of these pages by regex all week — the
    # architecture diagram, the comparison table, the badges, the technical block —
    # and one of those cuts took a `</div>` with it. Browsers auto-close, so the page
    # looked fine and the mistake rode into production unnoticed; it was found only
    # when something else was being checked. A parser answers in milliseconds what
    # eyes do not answer at all.
    from html.parser import HTMLParser

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "source", "track", "wbr"}

    class _Nesting(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.stack: list[tuple[str, int]] = []
            self.errors: list[str] = []

        def handle_starttag(self, tag, attrs):
            if tag not in VOID:
                self.stack.append((tag, self.getpos()[0]))

        def handle_endtag(self, tag):
            if tag in VOID:
                return
            if self.stack and self.stack[-1][0] == tag:
                self.stack.pop()
            elif self.stack:
                top, line = self.stack[-1]
                self.errors.append(
                    f"line {self.getpos()[0]}: </{tag}> while <{top}> from line {line} is open")

    for name in HTML_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        parser = _Nesting()
        parser.feed(path.read_text(encoding="utf-8"))
        unclosed = [f"<{t}> line {l}" for t, l in parser.stack if t not in ("html", "body")]
        if parser.errors or unclosed:
            ok = False
            detail = (parser.errors + [f"never closed: {u}" for u in unclosed])[:3]
            print(f"FAIL {name}: mismatched HTML nesting — " + "; ".join(detail))


    # `backdrop-filter` (like `transform` and `filter`) makes an element the
    # containing block for its position:fixed descendants. `.page-nav` had one, so
    # the mobile menu — `.nav-panel { position: fixed; inset: 0 }`, a child of that
    # bar — sized itself to the 56px bar instead of the viewport and rendered as a
    # strip across the top. Nothing in the markup or in the panel's own rules was
    # wrong, which is why it took a screenshot to notice.
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    if re.search(r"\.nav-panel\s*\{[^}]*position:\s*fixed", css, re.S):
        mobile = re.search(r"@media \(max-width: 640px\) \{.*", css, re.S)
        scoped = mobile.group(0) if mobile else ""
        if not re.search(r"\.page-nav\s*\{[^}]*backdrop-filter:\s*none", scoped, re.S):
            ok = False
            print("FAIL styles.css: .page-nav keeps a backdrop-filter where .nav-panel is "
                  "position:fixed — the overlay will size to the 56px bar, not the viewport. "
                  "Set `backdrop-filter: none` on .page-nav inside the mobile query.")


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


    # The third layer, and the one that actually bit: the constant above versions
    # the *sessionStorage* key, but the fetch URL was a bare "/i18n/en.json". That
    # path is served with stale-while-revalidate=86400, so a browser answers from a
    # day-old copy instantly — and site.js then files that stale dictionary under
    # the fresh key. Marker moved, words did not. A section removed from the repo,
    # the deploy and the live JSON was still on screen for exactly this reason.
    # Putting the version in the URL makes the stale entry unreachable instead of
    # merely discouraged, so the URL must carry it.
    if "/i18n/" in site and not re.search(
            r'fetch\(\s*"/i18n/"\s*\+\s*lang\s*\+\s*"\.json\?v="\s*\+\s*I18N_CACHE_VER',
            site):
        ok = False
        print("FAIL site.js: the locale fetch URL does not carry I18N_CACHE_VER — "
              "stale-while-revalidate can serve a day-old dictionary under the new "
              'cache key. Fetch "/i18n/" + lang + ".json?v=" + I18N_CACHE_VER.')


    # A privacy policy's "Last Updated" is not decoration — it states when users
    # were told something. On 2026-08-12 the policy's definition of the User ID was
    # corrected, a Device ID entry was added and video calling was removed from it,
    # and the line still read "July 27, 2026". Nobody lied; a hand-maintained date
    # just does not move on its own. Same fix as the cache markers: stamp what the
    # date refers to, and fail when the text moves without it.
    stamp_file = ROOT / "scripts/.privacy-stamp"
    raw = stamp_file.read_text(encoding="utf-8").split() if stamp_file.exists() else []
    h = hashlib.sha256()
    for lang in LANGS:
        d = load_dict(lang)
        for key in sorted(k for k in d
                          if k.startswith("privacy.") and k != "privacy.privacy-policy.p2"):
            h.update(key.encode() + b"\x00" + d[key].encode() + b"\x00")
    want_stamp = h.hexdigest()[:12]
    if len(raw) != 2:
        ok = False
        print("FAIL scripts/.privacy-stamp is missing or malformed — "
              "run `python3 scripts/stamp-privacy.py`.")
    elif raw[1] != want_stamp:
        ok = False
        print(f"FAIL privacy policy text changed ({raw[1]} -> {want_stamp}) but "
              f'"Last Updated" still says {raw[0]}. If the change was substantive, run '
              "`python3 scripts/stamp-privacy.py`; if it was a typo fix, run it anyway — "
              "a date that is slightly too recent is honest, one that is stale is not.")


    # Same failure one layer up: I18N_CACHE_VER is derived from the locale files,
    # but site.js itself was served from cache (vercel.json allows a day of
    # stale-while-revalidate) and styles.css carried a hand-typed ?v= that nobody
    # moved. A derived version marker is useless if the file carrying it is stale.
    # Both query strings are now content hashes and are checked here.
    import hashlib as _hl

    def _h10(name):
        return _hl.sha256((ROOT / name).read_bytes()).hexdigest()[:10]

    for asset, pattern in (("styles.css", r"styles\.css\?v=([0-9a-z-]+)"),
                           ("site.js", r'src="/site\.js\?v=([0-9a-z]+)"')):
        expect = _h10(asset)
        for name in HTML_FILES:
            text = (ROOT / name).read_text(encoding="utf-8")
            found = set(re.findall(pattern, text))
            if not found:
                ok = False
                print(f"FAIL {name}: no content-hash version on {asset}")
            elif found != {expect}:
                ok = False
                print(f'FAIL {name}: {asset}?v={sorted(found)[0]} but it hashes to '
                      f'"{expect}" — browsers will keep the cached file.')

    if ok:
        print(f"OK: {len(base)} keys × {len(LANGS)} langs; {len(used)} HTML refs")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
