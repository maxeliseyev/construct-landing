#!/usr/bin/env python3
"""
One-shot / repeatable migrator: class-based .en/.ru/.ja siblings → data-i18n
+ JSON locale files.

Usage (from repo root):
  python3 scripts/migrate-i18n.py              # write i18n/*.json + rewrite HTML
  python3 scripts/migrate-i18n.py --dry-run    # report only
  python3 scripts/migrate-i18n.py --json-only  # only refresh JSON from current HTML

Parses a simplified HTML tokenizer (good enough for our static pages).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "i18n"
LANGS = ("en", "ru", "ja")

PAGES = {
    "index.html": "home",
    "faq.html": "faq",
}

# Tags that may carry locale classes in our pages.
LOCALE_TAGS = {"span", "p", "ul", "li", "h1", "h2", "h3", "h4", "td", "th", "a", "div", "strong", "em"}


@dataclass
class Token:
    kind: str  # start | end | text | comment | doctype | other
    value: str
    tag: str = ""
    attrs: Dict[str, str] = field(default_factory=dict)
    self_closing: bool = False


def parse_attrs(s: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    # class="foo bar" | class='x' | id=foo | data-x="y"
    for m in re.finditer(
        r'([:@A-Za-z_][\w:.-]*)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+))',
        s,
    ):
        key = m.group(1)
        val = m.group(3) if m.group(3) is not None else (
            m.group(4) if m.group(4) is not None else m.group(5)
        )
        attrs[key] = val
    return attrs


def tokenize(html: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(html)
    while i < n:
        if html.startswith("<!--", i):
            j = html.find("-->", i + 4)
            if j < 0:
                tokens.append(Token("comment", html[i:]))
                break
            tokens.append(Token("comment", html[i : j + 3]))
            i = j + 3
            continue
        if html.startswith("<!", i):
            j = html.find(">", i)
            if j < 0:
                tokens.append(Token("other", html[i:]))
                break
            tokens.append(Token("doctype", html[i : j + 1]))
            i = j + 1
            continue
        if html[i] == "<":
            j = html.find(">", i)
            if j < 0:
                tokens.append(Token("text", html[i:]))
                break
            raw = html[i : j + 1]
            # handle `</span` split across lines already included until >
            if raw.startswith("</"):
                m = re.match(r"</\s*([A-Za-z][\w:-]*)\s*>", raw)
                tag = m.group(1).lower() if m else ""
                tokens.append(Token("end", raw, tag=tag))
            else:
                m = re.match(r"<\s*([A-Za-z][\w:-]*)([^>]*)>", raw)
                if m:
                    tag = m.group(1).lower()
                    rest = m.group(2)
                    self_closing = rest.rstrip().endswith("/")
                    attrs = parse_attrs(rest)
                    tokens.append(
                        Token("start", raw, tag=tag, attrs=attrs, self_closing=self_closing)
                    )
                else:
                    tokens.append(Token("other", raw))
            i = j + 1
            continue
        j = html.find("<", i)
        if j < 0:
            tokens.append(Token("text", html[i:]))
            break
        tokens.append(Token("text", html[i:j]))
        i = j
    return tokens


def class_list(attrs: Dict[str, str]) -> List[str]:
    return [c for c in attrs.get("class", "").split() if c]


def locale_of(attrs: Dict[str, str]) -> Optional[str]:
    classes = class_list(attrs)
    for lang in LANGS:
        if lang in classes:
            return lang
    return None


def serialize_start(tag: str, attrs: Dict[str, str], self_closing: bool = False) -> str:
    parts = [f"<{tag}"]
    for k, v in attrs.items():
        # preserve attribute order approximately via dict insertion
        if v is None:
            continue
        esc = v.replace('"', "&quot;")
        parts.append(f' {k}="{esc}"')
    if self_closing:
        parts.append(" />")
    else:
        parts.append(">")
    return "".join(parts)


def normalize_inner(html: str) -> str:
    """Collapse purely decorative whitespace between tags; keep text spaces."""
    s = html.strip()
    # compress whitespace-only runs that include newlines between tags
    s = re.sub(r">\s+<", "><", s)
    # collapse internal multi-spaces in text nodes carefully: keep single spaces
    s = re.sub(r"[ \t]+\n[ \t]+", " ", s)
    s = re.sub(r"\s+\n\s+", " ", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def is_plain_text(inner: str) -> bool:
    return "<" not in inner


def slugify(text: str, max_len: int = 40) -> str:
    t = re.sub(r"<[^>]+>", "", text)
    t = t.strip().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if not t:
        return "item"
    return t[:max_len].rstrip("-")


@dataclass
class LocaleNode:
    start_idx: int
    end_idx: int  # inclusive
    tag: str
    attrs: Dict[str, str]
    lang: str
    inner: str


def find_matching_end(tokens: List[Token], start: int) -> int:
    """Return index of the end token matching tokens[start] start tag."""
    assert tokens[start].kind == "start"
    tag = tokens[start].tag
    if tokens[start].self_closing or tag in {
        "br", "hr", "img", "input", "meta", "link", "source", "wbr", "area", "base", "col", "embed", "param", "track"
    }:
        return start
    depth = 0
    for i in range(start, len(tokens)):
        tok = tokens[i]
        if tok.kind == "start" and tok.tag == tag and not tok.self_closing:
            depth += 1
        elif tok.kind == "end" and tok.tag == tag:
            depth -= 1
            if depth == 0:
                return i
    return start


def inner_html(tokens: List[Token], start: int, end: int) -> str:
    if end <= start + 1:
        return ""
    return "".join(t.value for t in tokens[start + 1 : end])


def extract_groups(tokens: List[Token]) -> List[Dict[str, LocaleNode]]:
    """Find consecutive locale siblings of the same tag.

    Supports:
      en, ru, ja
      en, en, ru, ru, ja, ja   (zip by index)
      en, ru, ja, en, ru, ja
    Separators between siblings: whitespace-only text nodes only.
    """
    groups: List[Dict[str, LocaleNode]] = []
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if tok.kind != "start" or tok.tag not in LOCALE_TAGS:
            i += 1
            continue
        lang = locale_of(tok.attrs)
        if not lang:
            i += 1
            continue

        # Collect a run of locale-classed elements of the SAME tag.
        nodes: List[LocaleNode] = []
        j = i
        tag0 = tok.tag
        while j < n:
            t = tokens[j]
            if t.kind == "text" and t.value.strip() == "":
                j += 1
                continue
            if t.kind != "start" or t.tag != tag0:
                break
            l = locale_of(t.attrs)
            if not l:
                break
            end = find_matching_end(tokens, j)
            nodes.append(
                LocaleNode(
                    start_idx=j,
                    end_idx=end,
                    tag=t.tag,
                    attrs=dict(t.attrs),
                    lang=l,
                    inner=inner_html(tokens, j, end),
                )
            )
            j = end + 1
            while j < n and tokens[j].kind == "text" and tokens[j].value.strip() == "":
                j += 1

        by_lang: Dict[str, List[LocaleNode]] = {l: [] for l in LANGS}
        for node in nodes:
            if node.lang in by_lang:
                by_lang[node.lang].append(node)

        counts = [len(by_lang[l]) for l in LANGS]
        if counts[0] > 0 and counts[0] == counts[1] == counts[2]:
            for k in range(counts[0]):
                groups.append({l: by_lang[l][k] for l in LANGS})
            i = max(node.end_idx for node in nodes) + 1
        else:
            # Incomplete run — advance past first node only so nested/other
            # patterns can still be found later.
            i = nodes[0].end_idx + 1 if nodes else i + 1
    return groups


def nearest_section_prefix(tokens: List[Token], idx: int, page_ns: str) -> str:
    """Walk backward for id= on section/h2/h3 or data-i18n-page section markers."""
    for k in range(idx, -1, -1):
        t = tokens[k]
        if t.kind != "start":
            continue
        if t.tag in {"section", "header", "footer", "main", "nav", "h2", "h3", "h1"}:
            eid = t.attrs.get("id") or t.attrs.get("aria-labelledby") or ""
            if eid:
                eid = re.sub(r"-heading$", "", eid)
                eid = re.sub(r"^section-", "", eid)
                return f"{page_ns}.{eid}"
    return page_ns


def assign_keys(
    groups: List[Dict[str, LocaleNode]], tokens: List[Token], page_ns: str
) -> List[Tuple[str, Dict[str, LocaleNode], bool]]:
    """Return list of (key, group, is_html)."""
    counters: Dict[str, int] = {}
    out = []
    used = set()

    for g in groups:
        en = g["en"]
        prefix = nearest_section_prefix(tokens, en.start_idx, page_ns)
        plain = is_plain_text(en.inner)
        base_slug = slugify(en.inner if plain else re.sub(r"<[^>]+>", " ", en.inner))
        # Prefer tag role
        if en.tag in {"h1", "h2", "h3", "h4"}:
            role = "title"
        elif en.tag == "ul":
            role = "list"
        elif en.tag == "p":
            role = "p"
        elif en.tag == "summary" or (
            en.tag == "span" and any(
                tokens[k].tag == "summary"
                for k in range(max(0, en.start_idx - 5), en.start_idx)
                if tokens[k].kind == "start"
            )
        ):
            role = "q"
        else:
            role = "t"

        counters.setdefault(prefix, 0)
        counters[prefix] += 1
        n = counters[prefix]

        if role == "title" and n == 1:
            key = f"{prefix}.title"
        elif role == "q":
            key = f"{prefix}.q{n}"
        elif role == "list":
            key = f"{prefix}.list{n}"
        elif role == "p":
            key = f"{prefix}.p{n}"
        else:
            key = f"{prefix}.{role}{n}"
            if base_slug and base_slug not in {"item"}:
                # try readable short keys for short labels
                if plain and len(en.inner.strip()) < 48:
                    cand = f"{prefix}.{base_slug}"
                    if cand not in used:
                        key = cand

        # ensure unique
        orig = key
        suffix = 2
        while key in used:
            key = f"{orig}-{suffix}"
            suffix += 1
        used.add(key)

        is_html = not plain
        # Also treat as html if any lang has tags
        for lang in LANGS:
            if not is_plain_text(g[lang].inner):
                is_html = True
        out.append((key, g, is_html))
    return out


def rebuild_html(
    tokens: List[Token],
    keyed: List[Tuple[str, Dict[str, LocaleNode], bool]],
) -> str:
    """Replace each en node with a data-i18n node; drop matching ru/ja nodes.

    Only the exact token ranges of locale nodes are removed — never the full
    span between min/max (that would delete interleaved second paragraphs).
    """
    skip = set()
    replace_at: Dict[int, Tuple[str, str, Dict[str, str], str, bool]] = {}

    for key, g, is_html in keyed:
        en = g["en"]
        attrs = dict(en.attrs)
        classes = [c for c in class_list(attrs) if c not in LANGS]
        if classes:
            attrs["class"] = " ".join(classes)
        else:
            attrs.pop("class", None)
        if is_html:
            attrs["data-i18n-html"] = key
            attrs.pop("data-i18n", None)
        else:
            attrs["data-i18n"] = key
            attrs.pop("data-i18n-html", None)

        replace_at[en.start_idx] = (key, en.tag, attrs, en.inner, is_html)

        for lang, node in g.items():
            for i in range(node.start_idx, node.end_idx + 1):
                if lang == "en" and i == en.start_idx:
                    continue  # replaced, not skipped
                skip.add(i)
            # Drop one trailing whitespace text node after removed non-en blocks
            # to avoid huge blank gaps (safe no-op if next token is real content).
            if lang != "en":
                after = node.end_idx + 1
                if (
                    after < len(tokens)
                    and tokens[after].kind == "text"
                    and tokens[after].value.strip() == ""
                ):
                    skip.add(after)

    out: List[str] = []
    i = 0
    while i < len(tokens):
        if i in replace_at:
            _key, tag, attrs, inner, is_html = replace_at[i]
            body = normalize_inner(inner)
            if is_html:
                out.append(serialize_start(tag, attrs) + body + f"</{tag}>")
            else:
                text = re.sub(r"<[^>]+>", "", body)
                text = re.sub(r"\s+", " ", text).strip()
                out.append(serialize_start(tag, attrs) + text + f"</{tag}>")
            # advance past the original en element tokens
            en_end = None
            for key2, g2, _ in keyed:
                if g2["en"].start_idx == i:
                    en_end = g2["en"].end_idx
                    break
            i = (en_end + 1) if en_end is not None else i + 1
            continue
        if i in skip:
            i += 1
            continue
        out.append(tokens[i].value)
        i += 1
    return "".join(out)


def strip_legacy_lang_css(html: str) -> str:
    # Remove common visibility blocks for en/ru/ja
    patterns = [
        r"html:not\(\[data-lang=\"en\"\]\)\s*\.en\s*,\s*"
        r"html:not\(\[data-lang=\"ru\"\]\)\s*\.ru\s*,\s*"
        r"html:not\(\[data-lang=\"ja\"\]\)\s*\.ja\s*\{[^}]*\}",
        r"html\[data-lang=\"en\"\]\s*\.ru\s*,\s*html\[data-lang=\"ru\"\]\s*\.en\s*\{[^}]*\}",
    ]
    for p in patterns:
        html = re.sub(p, "", html, flags=re.S)
    return html


def ensure_page_attr(html: str, page_ns: str) -> str:
    if 'data-i18n-page=' in html:
        return html
    return re.sub(
        r"(<html\b)([^>]*)(>)",
        rf'\1\2 data-i18n-page="{page_ns}"\3',
        html,
        count=1,
        flags=re.I,
    )


def process_page(
    rel: str, page_ns: str, dry_run: bool, json_only: bool
) -> Tuple[Dict[str, Dict[str, str]], int]:
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    tokens = tokenize(html)
    groups = extract_groups(tokens)
    keyed = assign_keys(groups, tokens, page_ns)

    per_lang: Dict[str, Dict[str, str]] = {l: {} for l in LANGS}
    for key, g, is_html in keyed:
        for lang in LANGS:
            val = normalize_inner(g[lang].inner)
            if not is_html:
                val = re.sub(r"<[^>]+>", "", val)
                val = re.sub(r"\s+", " ", val).strip()
            per_lang[lang][key] = val

    # titles from data-title-* 
    m_en = re.search(r'data-title-en="([^"]*)"', html)
    m_ru = re.search(r'data-title-ru="([^"]*)"', html)
    m_ja = re.search(r'data-title-ja="([^"]*)"', html)
    if m_en:
        per_lang["en"][f"{page_ns}.meta.title"] = m_en.group(1)
    if m_ru:
        per_lang["ru"][f"{page_ns}.meta.title"] = m_ru.group(1)
    if m_ja:
        per_lang["ja"][f"{page_ns}.meta.title"] = m_ja.group(1)

    print(f"{rel}: {len(keyed)} locale groups → keys")
    if dry_run:
        for key, g, is_html in keyed[:8]:
            sample = re.sub(r"\s+", " ", g["en"].inner)[:70]
            print(f"  {key}  html={is_html}  {sample!r}")
        if len(keyed) > 8:
            print(f"  … +{len(keyed) - 8} more")
        return per_lang, len(keyed)

    if not json_only:
        new_html = rebuild_html(tokens, keyed)
        new_html = strip_legacy_lang_css(new_html)
        new_html = ensure_page_attr(new_html, page_ns)
        path.write_text(new_html, encoding="utf-8")
        print(f"  wrote {rel}")

    return per_lang, len(keyed)


def merge_dicts(dst: Dict[str, str], src: Dict[str, str]) -> None:
    for k, v in src.items():
        dst[k] = v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    combined: Dict[str, Dict[str, str]] = {l: {} for l in LANGS}
    total = 0
    for rel, ns in PAGES.items():
        if not (ROOT / rel).exists():
            print(f"skip missing {rel}", file=sys.stderr)
            continue
        per_lang, n = process_page(rel, ns, args.dry_run, args.json_only)
        total += n
        for lang in LANGS:
            merge_dicts(combined[lang], per_lang[lang])

    if args.dry_run:
        print(f"total groups: {total}")
        return 0

    I18N_DIR.mkdir(exist_ok=True)
    for lang in LANGS:
        # stable key order
        ordered = {k: combined[lang][k] for k in sorted(combined[lang].keys())}
        out = I18N_DIR / f"{lang}.json"
        out.write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out.relative_to(ROOT)} ({len(ordered)} keys)")

    # quick parity
    keys = [set(combined[l].keys()) for l in LANGS]
    if not keys[0] == keys[1] == keys[2]:
        print("WARNING: key parity mismatch", file=sys.stderr)
        for a, b in (("en", "ru"), ("en", "ja")):
            only_a = keys[LANGS.index(a)] - keys[LANGS.index(b)]
            only_b = keys[LANGS.index(b)] - keys[LANGS.index(a)]
            if only_a:
                print(f"  only {a}: {sorted(only_a)[:10]}", file=sys.stderr)
            if only_b:
                print(f"  only {b}: {sorted(only_b)[:10]}", file=sys.stderr)
        return 1
    print(f"OK: {len(keys[0])} keys × {len(LANGS)} langs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
