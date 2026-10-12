#!/usr/bin/env python3
"""Build the site into dist/: every content page once per language, at its own URL.

    python3 scripts/build-locales.py           # repo -> dist/   (Vercel runs this)
    python3 scripts/build-locales.py --check   # build into a temp dir, verify, discard

English stays where it always was (/, /faq, …); every other language gets a
prefix (/ru/faq, /tr/). Each page is rendered with its text, <html lang>, title,
description, link-preview tags, canonical and hreflang already in the HTML, so a
search engine, a chat app unfurling a link and a reader without JavaScript all
get the language the URL names. Before this the HTML was English everywhere
and site.js swapped the words in after load — invisible to all three.

/add and /c/… are not rendered per language: the app's Universal Links and
invite links point at them, so they keep translating at runtime.

What the renderer does to an element is what applyI18n in site.js used to do in
the browser — textContent for data-i18n, innerHTML for data-i18n-html, the
Russian widow fix, the glitch label's data-text — and the output is verified
against the dictionaries after every build, not trusted. `--check` also runs the
widow fix from site.js under node, when node is installed, and compares.

Python 3.12 runs the build on Vercel; keep this stdlib-only and 3.12-compatible.
See ~/Code/construct-docs/decisions/landing-locale-urls.md.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORIGIN = "https://konstruct.cc"

# Source file -> English path. Same list as PAGES in lang-redirect.js and the
# :page(…) group in vercel.json; verify() fails when they disagree.
PAGES = {
    "index.html": "/",
    "faq.html": "/faq",
    "technical.html": "/technical",
    "roadmap.html": "/roadmap",
    "privacy.html": "/privacy",
}

# Locales a native speaker has read. The others are machine translations from
# the Russian: rendered and reachable, but `noindex`, out of the sitemap and out
# of the hreflang set until someone who speaks the language signs them off —
# a public, indexed, linkable page is a different promise from text shown only
# to people whose browser asked for it. Adding a code here is that sign-off.
REVIEWED = ("en", "ru")

OG_LOCALE = {"en": "en_US", "ru": "ru_RU", "fr": "fr_FR", "tr": "tr_TR",
             "uk": "uk_UA", "hy": "hy_AM", "ja": "ja_JP"}

# Kept out of dist/: tooling that production served by accident before there
# was a build (konstruct.cc/scripts/check-i18n.py answered 200), plus whatever
# .vercelignore lists. Matched by name at any depth.
TOOLING = {"scripts", "tests", ".githooks", "dist", "node_modules", "README.md",
           "AGENTS.md", "CLAUDE.md", "vercel.json", ".vercelignore",
           ".gitignore", ".DS_Store", "__pycache__", "speculation-rules.json"}

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


class BuildError(Exception):
    pass


# ── Inputs ───────────────────────────────────────────────────────────────────

def site_list(name: str) -> list[str] | dict[str, str]:
    """Read SUPPORTED / LABELS from site.js, so the language list lives once."""
    src = (ROOT / "site.js").read_text(encoding="utf-8")
    if name == "SUPPORTED":
        m = re.search(r"var SUPPORTED = \[([^\]]*)\];", src)
        return re.findall(r'"(\w+)"', m.group(1))
    m = re.search(rf"var {name} = \{{(.*?)\}};", src, re.S)
    return dict(re.findall(r'(\w+): "([^"]*)"', m.group(1)))


LANGS: list[str] = site_list("SUPPORTED")       # menu order, "en" first
LABELS: dict[str, str] = site_list("LABELS")


def load(lang: str) -> dict[str, str]:
    return json.loads((ROOT / f"i18n/{lang}.json").read_text(encoding="utf-8"))


def url(lang: str, path: str) -> str:
    """/faq in English, /ru/faq in Russian; / and /ru for the home page."""
    if lang == "en":
        return path
    return f"/{lang}" + ("" if path == "/" else path)


def out_name(lang: str, page: str) -> str:
    return page if lang == "en" else f"{lang}/{page}"


# ── The browser's rules, ported ──────────────────────────────────────────────
# Must stay character-for-character the regex in site.js; --check compares them
# under node.

WIDOW_WORDS = ("а|без|бы|в|во|для|до|за|и|из|или|к|ко|ли|на|не|ни|но|о|"
               "об|обо|от|по|под|при|про|с|со|у|через")
WIDOW_RE = re.compile(r"(^|[\s ])(" + WIDOW_WORDS + r")[ \t]+", re.I)


def fix_widows(text: str, lang: str) -> str:
    if lang != "ru":
        return text
    # JS replace() with /g does not rescan replaced text either, so "в и в"
    # behaves the same: each match consumes its trailing space.
    return WIDOW_RE.sub("\\1\\2 ", text)


def fix_widows_html(markup: str, lang: str) -> str:
    if lang != "ru":
        return markup
    out, verbatim = [], 0
    for chunk in re.findall(r"<[^>]*>|[^<]+", markup):
        if not chunk.startswith("<"):
            out.append(chunk if verbatim else fix_widows(chunk, lang))
            continue
        if re.match(r"<\s*(code|pre)\b", chunk, re.I):
            verbatim += 1
        elif re.match(r"<\s*/\s*(code|pre)\b", chunk, re.I):
            verbatim = max(0, verbatim - 1)
        out.append(chunk)
    return "".join(out)


# ── Finding the translated elements ──────────────────────────────────────────

class Marked(HTMLParser):
    """Character offsets of every data-i18n / data-i18n-html element.

    A regex cannot find where an element ends; a parser can. The source pages
    are strictly nested (check-i18n fails otherwise), so a mismatch here is a
    bug and stops the build rather than producing a page with the translation
    spliced into the wrong place.
    """

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.line_at = [0]
        for m in re.finditer("\n", text):
            self.line_at.append(m.end())
        self.stack: list[tuple] = []
        self.found: list[dict] = []
        self.feed(text)
        self.close()

    def _offset(self) -> int:
        line, col = self.getpos()
        return self.line_at[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._offset()
        raw = self.get_starttag_text()
        a = dict(attrs)
        mark = None
        if "data-i18n" in a:
            mark = ("text", a["data-i18n"])
        elif "data-i18n-html" in a:
            mark = ("html", a["data-i18n-html"])
        if tag in VOID:
            if mark:
                raise BuildError(f"<{tag}> carries {mark[1]} but cannot hold text")
            return
        self.stack.append((tag, start, start + len(raw), mark))

    def handle_startendtag(self, tag, attrs):
        if "data-i18n" in dict(attrs) or "data-i18n-html" in dict(attrs):
            raise BuildError(f"self-closing <{tag}/> carries an i18n key")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            open_tag = self.stack[-1][0] if self.stack else None
            raise BuildError(f"line {self.getpos()[0]}: </{tag}> closes <{open_tag}>")
        name, start, open_end, mark = self.stack.pop()
        if mark:
            self.found.append({"tag": name, "start": start, "open_end": open_end,
                               "close": self._offset(), "kind": mark[0], "key": mark[1]})


# ── Rendering ────────────────────────────────────────────────────────────────

def fill(src: str, lang: str, d: dict[str, str]) -> str:
    """Put the translation into every marked element, innermost-safe."""
    marks = sorted(Marked(src).found, key=lambda m: m["start"])
    outer, reach = [], -1
    for m in marks:
        if m["start"] >= reach:          # an element inside a replaced one is gone
            outer.append(m)
            reach = m["close"]
    for m in reversed(outer):
        value = d.get(m["key"])
        if value is None:                # same as the browser: keep the English
            continue
        open_tag = src[m["start"]:m["open_end"]]
        if m["kind"] == "text":
            value = fix_widows(value, lang)
            inner = html.escape(value, quote=False)
            # The glitch label draws its ghost layers from data-text.
            open_tag = re.sub(r'(\sdata-text=)"[^"]*"',
                              lambda x: f'{x.group(1)}"{html.escape(value)}"', open_tag)
        else:
            inner = fix_widows_html(value, lang)
        src = src[:m["start"]] + open_tag + inner + src[m["close"]:]
    return src


def attr_escape(text: str) -> str:
    return html.escape(text, quote=True)


def head_block(lang: str, path: str, title: str, desc: str) -> str:
    """Canonical, alternates and link-preview tags for one page in one language."""
    self_url = ORIGIN + url(lang, path)
    t, dsc = attr_escape(title), attr_escape(desc)
    lines = []
    if lang not in REVIEWED:
        lines.append('<meta name="robots" content="noindex" />')
    lines.append(f'<link rel="canonical" href="{self_url}" />')
    if lang in REVIEWED:
        for alt in LANGS:
            if alt in REVIEWED:
                lines.append(f'<link rel="alternate" hreflang="{alt}" '
                             f'href="{ORIGIN + url(alt, path)}" />')
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN + path}" />')
    lines += [
        '<meta property="og:type" content="website" />',
        '<meta property="og:site_name" content="Konstruct" />',
        f'<meta property="og:url" content="{self_url}" />',
        f'<meta property="og:title" content="{t}" />',
        f'<meta property="og:description" content="{dsc}" />',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}" />',
    ]
    lines += [f'<meta property="og:locale:alternate" content="{OG_LOCALE[a]}" />'
              for a in LANGS if a != lang and a in REVIEWED and lang in REVIEWED]
    lines += [
        f'<meta property="og:image" content="{ORIGIN}/og-image.png" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{t}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{t}" />',
        f'<meta name="twitter:description" content="{dsc}" />',
        f'<meta name="twitter:image" content="{ORIGIN}/og-image.png" />',
    ]
    return "\n        ".join(lines)


INTERNAL = "|".join(re.escape(p) for p in PAGES.values())
INTERNAL_LINK = re.compile(rf'(\shref=)"({INTERNAL})([?#][^"]*)?"')
RELATIVE = re.compile(r'(\s(?:src|href))="(?![a-zA-Z][a-zA-Z0-9+.-]*:|/|#)([^"]+)"')


def prefix_links(markup: str, lang: str) -> str:
    """Keep a reader in their language: /faq -> /ru/faq. /add and /c/… stay."""
    if lang == "en":
        return markup
    return INTERNAL_LINK.sub(lambda m: f'{m.group(1)}"{url(lang, m.group(2))}{m.group(3) or ""}"',
                             markup)


def render(page: str, lang: str, d: dict[str, str]) -> str:
    path = PAGES[page]
    src = (ROOT / page).read_text(encoding="utf-8")
    ns = re.search(r'data-i18n-page="([^"]+)"', src).group(1)

    out = fill(src, lang, d)

    # <html>: the language, and the marker that tells site.js not to translate.
    def html_tag(m: re.Match) -> str:
        tag = re.sub(r'(\slang=)"[^"]*"', rf'\1"{lang}"', m.group(0), count=1)
        tag = re.sub(r'(\sdata-lang=)"[^"]*"', rf'\1"{lang}"', tag, count=1)
        return tag[:-1].rstrip() + "\n    data-prerendered\n>"
    out = re.sub(r"<html\b[^>]*>", html_tag, out, count=1)

    title = d.get(f"{ns}.meta.title")
    desc = d.get(f"{ns}.meta.description")
    if not title or not desc:
        raise BuildError(f"{lang}: {ns}.meta.title / {ns}.meta.description missing")
    out = re.sub(r"<title>[^<]*</title>", f"<title>{html.escape(title, quote=False)}</title>",
                 out, count=1)
    out, n = re.subn(r'<meta\s+name="description"\s+content="[^"]*"\s*/>',
                     f'<meta name="description" content="{attr_escape(desc)}" />\n        '
                     + head_block(lang, path, title, desc), out, count=1)
    if n != 1:
        raise BuildError(f"{page}: no <meta name=\"description\"> to anchor the head block")

    out = prefix_links(out, lang)

    # The switcher: each entry is this page in that language.
    def switch(m: re.Match) -> str:
        alt, ws = m.group(2), m.group(1)
        extra = f'{ws}class="active"{ws}aria-current="true"' if alt == lang else ""
        return (f'<a{ws}href="{url(alt, path)}"{ws}hreflang="{alt}"{ws}lang="{alt}"'
                f'{ws}data-lang-btn="{alt}"{extra}{m.group(3)}>')
    out, n = re.subn(r'<a(\s+)href="[^"]*"\s+hreflang="\w+"\s+lang="\w+"\s+'
                     r'data-lang-btn="(\w+)"(?:\s+class="active"\s+aria-current="true")?(\s*)>',
                     switch, out)
    if n != len(LANGS):
        raise BuildError(f"{page}: switcher has {n} entries, expected {len(LANGS)}")
    out = re.sub(r"(<span data-lang-current>)[^<]*(</span>)",
                 lambda m: m.group(1) + LABELS[lang] + m.group(2), out)

    if lang != "en":
        # The first-visit redirect only ever runs from English pages.
        out = re.sub(r'\n\s*<script src="/lang-redirect\.js[^"]*"></script>', "", out)

    # Relative asset paths would resolve under /ru/ and 404.
    out = RELATIVE.sub(r'\1="/\2"', out)
    return out


def sitemap() -> str:
    rows = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path in PAGES.values():
        for lang in LANGS:
            if lang not in REVIEWED:
                continue
            rows.append(f"  <url>\n    <loc>{ORIGIN + url(lang, path)}</loc>")
            for alt in LANGS:
                if alt in REVIEWED:
                    rows.append(f'    <xhtml:link rel="alternate" hreflang="{alt}" '
                                f'href="{ORIGIN + url(alt, path)}"/>')
            rows.append(f'    <xhtml:link rel="alternate" hreflang="x-default" '
                        f'href="{ORIGIN + path}"/>')
            rows.append("  </url>")
    rows.append("</urlset>")
    return "\n".join(rows) + "\n"


def speculation_rules() -> str:
    """Prerender same-language navigation on hover. Never the switcher: a
    prerendered English page would run lang-redirect.js before the click that
    records the choice, and land the reader back where they started."""
    hrefs = [url(lang, p) for lang in LANGS for p in PAGES.values()]
    rules = {"prerender": [{
        "where": {"and": [{"href_matches": hrefs},
                          {"not": {"selector_matches": "[data-lang-btn]"}}]},
        "eagerness": "moderate",
    }]}
    return json.dumps(rules, indent=2, ensure_ascii=False) + "\n"


# ── Build ────────────────────────────────────────────────────────────────────

def ignored() -> set[str]:
    path = ROOT / ".vercelignore"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    return {l.strip().rstrip("/") for l in lines if l.strip() and not l.startswith("#")}


def source_files() -> list[pathlib.Path]:
    """What git would deploy: tracked and new files, not the ignored ones.

    Locally the checkout also holds build output and downloads that .gitignore
    keeps out (target/, a font archive); Vercel's clone never has them. Asking
    git makes the local dist/ the same as the deployed one. Without git —
    a tarball, or a build image that drops .git — walk the tree.
    """
    try:
        res = subprocess.run(["git", "ls-files", "-z", "--cached", "--others",
                              "--exclude-standard"], cwd=ROOT, capture_output=True,
                             check=True)
        return [ROOT / p for p in sorted(res.stdout.decode().split("\0")) if p]
    except (OSError, subprocess.CalledProcessError):
        return sorted(ROOT.rglob("*"))


def copy_static(dist: pathlib.Path) -> int:
    skip_paths = ignored()
    count = 0
    for path in source_files():
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(part in TOOLING for part in rel.parts):
            continue
        if any(str(rel) == s or str(rel).startswith(s + "/") or part == s
               for s in skip_paths for part in rel.parts):
            continue
        if rel.parts[0].startswith(".") and rel.parts[0] != ".well-known":
            continue
        dest = dist / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        count += 1
    return count


def build(dist: pathlib.Path) -> None:
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True)
    copied = copy_static(dist)
    for lang in LANGS:
        d = load(lang)
        for page in PAGES:
            out = dist / out_name(lang, page)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render(page, lang, d), encoding="utf-8")
    (dist / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (dist / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n", encoding="utf-8")
    (dist / "speculation-rules.json").write_text(speculation_rules(), encoding="utf-8")
    print(f"built {len(LANGS)} languages × {len(PAGES)} pages "
          f"({', '.join(l for l in LANGS if l in REVIEWED)} indexed), "
          f"{copied} static files -> {dist.relative_to(ROOT) if dist.is_relative_to(ROOT) else dist}")


# ── Verification ─────────────────────────────────────────────────────────────

def strip_tags(markup: str) -> str:
    return html.unescape(re.sub(r"<[^>]*>", "", markup))


def verify(dist: pathlib.Path) -> list[str]:
    errors: list[str] = []
    err = errors.append

    if LANGS[0] != "en":
        err(f"site.js SUPPORTED must start with en, got {LANGS}")

    redirect = (ROOT / "lang-redirect.js").read_text(encoding="utf-8")
    m = re.search(r"var SUPPORTED = \[([^\]]*)\];", redirect)
    if not m or re.findall(r'"(\w+)"', m.group(1)) != LANGS:
        err("lang-redirect.js SUPPORTED differs from site.js SUPPORTED")
    want_paths = set(PAGES.values()) | {f"/{p}" for p in PAGES}
    got_paths = set(re.findall(r'^\s*"(/[^"]*)":', redirect, re.M))
    if got_paths != want_paths:
        err(f"lang-redirect.js PAGES {sorted(got_paths)} != build PAGES {sorted(want_paths)}")

    vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    non_en = sorted(l for l in LANGS if l != "en")
    pages = sorted(p.strip("/") for p in PAGES.values() if p != "/")
    for rule in vercel.get("rewrites", []) + vercel.get("headers", []):
        for group, want in (("lang", non_en), ("page", pages)):
            g = re.search(rf":{group}\(([^)]*)\)", rule["source"])
            if g and sorted(g.group(1).split("|")) != want:
                err(f"vercel.json {rule['source']}: :{group}(...) should list {'|'.join(want)}")

    dicts = {lang: load(lang) for lang in LANGS}
    for lang in LANGS:
        d = dicts[lang]
        for page, path in PAGES.items():
            name = out_name(lang, page)
            f = dist / name
            if not f.exists():
                err(f"{name}: not built")
                continue
            out = f.read_text(encoding="utf-8")
            try:
                marks = Marked(out).found
            except BuildError as e:
                err(f"{name}: {e}")
                continue
            src_keys = sorted(m["key"] for m in Marked((ROOT / page).read_text(encoding="utf-8")).found)
            if sorted(m["key"] for m in marks) != src_keys:
                err(f"{name}: translated elements differ from the source page")
            for m in marks:
                value = d.get(m["key"])
                if value is None:
                    continue
                inner = out[m["open_end"]:m["close"]]
                if m["kind"] == "text":
                    want, got = fix_widows(value, lang), html.unescape(inner)
                else:
                    want = strip_tags(prefix_links(" " + fix_widows_html(value, lang), lang))[1:]
                    got = strip_tags(inner)
                if want != got:
                    err(f"{name}: {m['key']} renders {got[:50]!r}, dictionary says {want[:50]!r}")
                    break

            if not re.search(rf'<html\b[^>]*\slang="{lang}"[^>]*data-prerendered', out):
                err(f"{name}: <html lang> is not {lang}")
            self_url = ORIGIN + url(lang, path)
            if f'<link rel="canonical" href="{self_url}" />' not in out:
                err(f"{name}: canonical is not {self_url}")
            if out.count('rel="canonical"') != 1:
                err(f"{name}: more than one canonical")
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', out))
            want_alts = ({a: ORIGIN + url(a, path) for a in LANGS if a in REVIEWED}
                         | {"x-default": ORIGIN + path}) if lang in REVIEWED else {}
            if alts != want_alts:
                err(f"{name}: hreflang {alts} != {want_alts}")
            if ('content="noindex"' in out) == (lang in REVIEWED):
                err(f"{name}: noindex should be {'absent' if lang in REVIEWED else 'present'}")
            if RELATIVE.search(out):
                err(f"{name}: relative URL left: {RELATIVE.search(out).group(0).strip()}")
            if lang != "en":
                body = re.sub(r"<a\s[^>]*data-lang-btn[^>]*>", "", out)
                leak = INTERNAL_LINK.search(body)
                if leak:
                    err(f"{name}: links to the English page {leak.group(2)}")
                if "lang-redirect.js" in out:
                    err(f"{name}: carries the first-visit redirect")

    smap = (dist / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", smap)
    want_locs = [ORIGIN + url(l, p) for p in PAGES.values() for l in LANGS if l in REVIEWED]
    if locs != want_locs:
        err(f"sitemap.xml lists {len(locs)} URLs, expected {len(want_locs)}")

    for leaked in ("scripts", ".githooks", "README.md", "vercel.json"):
        if (dist / leaked).exists():
            err(f"dist/{leaked} would be published")
    return errors


def node_widow_parity() -> list[str]:
    """Run site.js's own widow regex under node over every Russian value."""
    node = shutil.which("node")
    if not node:
        print("  (node not found — skipped the site.js widow parity check)")
        return []
    site = (ROOT / "site.js").read_text(encoding="utf-8")
    words = re.search(r'var WIDOW_WORDS = ((?:"[^"]*"\s*\+?\s*)+);', site)
    regex = re.search(r"var WIDOW_RE = (new RegExp\([^;]*\));", site)
    if not words or not regex:
        return ["site.js: WIDOW_WORDS / WIDOW_RE not found — the port cannot be compared"]
    values = list(load("ru").values())
    script = (f"var WIDOW_WORDS = {words.group(1)}; var WIDOW_RE = {regex.group(1)};"
              "var v = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
              "process.stdout.write(JSON.stringify(v.map(function (s) {"
              " return s.replace(WIDOW_RE, '$1$2\\u00A0'); })));")
    res = subprocess.run([node, "-e", script], input=json.dumps(values),
                         capture_output=True, text=True, check=False)
    if res.returncode:
        return [f"node: {res.stderr.strip()[:200]}"]
    js = json.loads(res.stdout)
    bad = [v for v, j in zip(values, js) if fix_widows(v, "ru") != j]
    return [f"widow fix differs from site.js on {len(bad)} value(s), e.g. {bad[0][:60]!r}"] if bad else []


def main() -> int:
    check = "--check" in sys.argv
    try:
        if check:
            with tempfile.TemporaryDirectory() as tmp:
                dist = pathlib.Path(tmp) / "dist"
                build(dist)
                errors = verify(dist) + node_widow_parity()
        else:
            dist = ROOT / "dist"
            build(dist)
            errors = verify(dist)
    except BuildError as e:
        errors = [str(e)]
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("OK: every page verified against the dictionaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
